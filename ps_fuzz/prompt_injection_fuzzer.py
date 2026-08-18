from .app_config import AppConfig
from .chat_clients import *
from .client_config import ClientConfig
from .attack_config import AttackConfig
from .test_base import TestStatus, StatusUpdate
from .test_base import TestBase
from .attack_registry import instantiate_tests
from .attack_loader import * # load and register attacks defined in 'attack/*.py'
from .work_progress_pool import WorkProgressPool, ThreadSafeTaskIterator, ProgressWorker
from .interactive_chat import *
from .results_table import print_table
import colorama
from pydantic import ValidationError
import logging
logger = logging.getLogger(__name__)

RESET = colorama.Style.RESET_ALL
LIGHTBLUE = colorama.Fore.LIGHTBLUE_EX
BRIGHT_RED = colorama.Fore.RED + colorama.Style.BRIGHT
BRIGHT_CYAN = colorama.Fore.CYAN + colorama.Style.BRIGHT
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
BRIGHT_YELLOW = colorama.Fore.LIGHTYELLOW_EX + colorama.Style.BRIGHT
ORANGE = colorama.Fore.LIGHTYELLOW_EX

def _build_client_kwargs(app_config: AppConfig, provider: str, model: str, temperature: float) -> dict:
    """Build kwargs for ClientLangChain based on provider and app config"""
    kwargs = {'model': model, 'temperature': temperature}
    
    # Add provider-specific base URLs if configured
    if provider == 'ollama' and hasattr(app_config, 'ollama_base_url') and app_config.ollama_base_url:
        kwargs['ollama_base_url'] = app_config.ollama_base_url
    elif provider == 'open_ai' and hasattr(app_config, 'openai_base_url') and app_config.openai_base_url:
        kwargs['openai_base_url'] = app_config.openai_base_url
    
    return kwargs

def _build_embedding_config(app_config: AppConfig) -> dict:
    """Build embedding configuration object with only embedding-specific properties"""
    return {
        'embedding_provider': getattr(app_config, 'embedding_provider', ''),
        'embedding_model': getattr(app_config, 'embedding_model', ''),
        'embedding_ollama_base_url': getattr(app_config, 'embedding_ollama_base_url', ''),
        'embedding_openai_base_url': getattr(app_config, 'embedding_openai_base_url', '')
    }

class TestTask(object):
    def __init__(self, test):
        self.test = test

    def __call__(self, progress_worker: ProgressWorker):
        result = self.test.run()
        if result and iter(result) is result:
            # Handle iterable results (e.g. status updates)
            for statusUpdate in self.test.run():
                color = RESET
                if statusUpdate.action == "Preparing":
                    color = LIGHTBLUE
                elif statusUpdate.action == "Attacking":
                    color = RED
                progress_worker.update(
                    task_name = f"{color}{statusUpdate.action}{RESET}: {statusUpdate.test_name}",
                    progress = statusUpdate.progress_position,
                    total = statusUpdate.progress_total,
                    colour = "BLUE"
                )
        elif result and isinstance(result, StatusUpdate):
            color = RESET
            if statusUpdate.action == "Preparing":
                color = LIGHTBLUE
            elif statusUpdate.action == "Attacking":
                color = RED
            statusUpdate = result
            progress_worker.update(
                task_name = f"{color}{statusUpdate.action}{RESET}: {statusUpdate.test_name}",
                progress = statusUpdate.progress_position,
                total = statusUpdate.progress_total,
                colour = "BLUE"
            )
        else:
            raise RuntimeError(f"BUG: Test {self.test.test_name} returned an unexpected result: {result}. Please fix the test run() function!")

def simpleProgressBar(progress, total, color, bar_length = 50):
    "Generate printable progress bar"
    if total > 0:
        filled_length = int(round(bar_length * progress / float(total)))
        bar = "█" * filled_length + '-' * (bar_length - filled_length)
        return f"[{color}{bar}{RESET}] {progress}/{total}"
    else:
        return f"[]"

def isResilient(test_status: TestStatus):
    "Define test as passed if there were no errors or failures during test run"
    return test_status.breach_count == 0 and test_status.error_count == 0 and test_status.skipped_count == 0

def isSkipped(test_status: TestStatus):
    "Define test as skipped if it has skipped count but no other results"
    return test_status.skipped_count > 0 and test_status.breach_count == 0 and test_status.resilient_count == 0 and test_status.error_count == 0

def fuzz_prompt_injections(client_config: ClientConfig, attack_config: AttackConfig, threads_count: int, custom_tests: List = None):
    print(f"{BRIGHT_CYAN}Running tests on your system prompt{RESET} ...")

    # Instantiate all tests
    has_custom_benchmark = client_config.custom_benchmark is not None
    tests: List[TestBase] = instantiate_tests(client_config, attack_config, custom_tests=custom_tests, custom_benchmark=has_custom_benchmark)

    # Create a thread pool to run tests within in parallel
    work_pool = WorkProgressPool(threads_count)

    # Wrap tests in a TestTask objects to be run in the thread pool
    test_tasks = map(TestTask, tests)

    # Run the tests (in parallel if num_of_threads > 1)
    # Known count of tests allows displaying the progress bar during execution
    work_pool.run(ThreadSafeTaskIterator(test_tasks), len(tests))

    # Report results
    RESILIENT = f"{GREEN}✔{RESET}"
    VULNERABLE = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"
    SKIPPED = f"{ORANGE}⊘{RESET}"

    print_table(
        title = "Test results",
        headers = [
            "",
            "Attack Type",
            "Broken",
            "Resilient",
            "Errors",
            "Skipped",
            "Strength",
        ],
        data = sorted([
            [
                SKIPPED if isSkipped(test.status) else ERROR if test.status.error_count > 0 else RESILIENT if isResilient(test.status) else VULNERABLE,
                f"{test.test_name + ' ':.<{50}}",
                test.status.breach_count,
                test.status.resilient_count,
                test.status.error_count,
                test.status.skipped_count,
                simpleProgressBar(test.status.resilient_count, test.status.total_count, GREEN if isResilient(test.status) else RED) if not isSkipped(test.status) else "N/A",
            ]
            for test in tests
        ], key=lambda x: x[1]),
        footer_row = [
                SKIPPED if all(isSkipped(test.status) for test in tests) else ERROR if all(test.status.error_count > 0 for test in tests) else RESILIENT if all(isResilient(test.status) for test in tests) else VULNERABLE,
                f"{'Total (# tests): ':.<50}",
                sum(test.status.breach_count > 0 for test in tests),
                sum(isResilient(test.status) for test in tests),
                sum(test.status.error_count > 0 for test in tests),
                sum(isSkipped(test.status) for test in tests),
                simpleProgressBar( # Total progress shows percentage of resilient tests among all tests
                    sum(isResilient(test.status) for test in tests),
                    len([test for test in tests if not isSkipped(test.status)]),
                    GREEN if all(isResilient(test.status) or isSkipped(test.status) for test in tests) else RED
                ),
        ]
    )

    resilient_tests_count = sum(isResilient(test.status) for test in tests)
    skipped_tests_count = sum(isSkipped(test.status) for test in tests)
    failed_tests = [f"{test.test_name}\n" if not isResilient(test.status) and not isSkipped(test.status) else "" for test in tests]
    skipped_tests = [f"{test.test_name}\n" if isSkipped(test.status) else "" for test in tests]

    total_tests_count = len(tests)
    executed_tests_count = total_tests_count - skipped_tests_count
    resilient_tests_percentage = resilient_tests_count / executed_tests_count * 100 if executed_tests_count > 0 else 0
    
    print(f"Your system prompt passed {int(resilient_tests_percentage)}% ({resilient_tests_count} out of {executed_tests_count}) of executed attack simulations.\n")
    
    if skipped_tests_count > 0:
        print(f"{ORANGE}{skipped_tests_count} test(s) were skipped{RESET} due to missing configuration or dependencies:\n{ORANGE}{''.join(skipped_tests)}{RESET}")
    
    if resilient_tests_count < executed_tests_count:
        print(f"Your system prompt {BRIGHT_RED}failed{RESET} the following tests:\n{RED}{''.join(failed_tests)}{RESET}\n")
    print(f"To learn about the various attack types, please consult the help section and the Prompt Security Fuzzer GitHub README.")
    print(f"You can also get a list of all available attack types by running the command '{BRIGHT}prompt-security-fuzzer --list-attacks{RESET}'.")

    # Print detailed test progress logs (TODO: select only some relevant representative entries and output to a "report" file, which is different from a debug .log file!)
    """
    for dynamic_test in dynamic_tests:
        print(f"Test: {dynamic_test.test_name}: {dynamic_test.test_description} ...")
        for entry in dynamic_test.status.log:
            print(f"Prompt: {entry.prompt}")
            print(f"Response: {entry.response}")
            print(f"Success: {entry.success}")
            print(f"Additional info: {entry.additional_info}")
    """

def run_interactive_chat(app_config: AppConfig):
    # Print current app configuration
    app_config.print_as_table()
    target_system_prompt = app_config.system_prompt
    try:
        kwargs = _build_client_kwargs(app_config, app_config.target_provider, app_config.target_model, 0)
        target_client = ClientLangChain(app_config.target_provider, **kwargs)
        interactive_chat(client=target_client, system_prompts=[target_system_prompt])
    except (ImportError, ValidationError) as e:
        logger.warning(f"Error accessing the Target LLM provider {app_config.target_provider} with model '{app_config.target_model}': {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return

def run_fuzzer(app_config: AppConfig):
    # Print current app configuration
    app_config.print_as_table()
    custom_benchmark = app_config.custom_benchmark
    target_system_prompt = app_config.system_prompt
    try:
        target_kwargs = _build_client_kwargs(app_config, app_config.target_provider, app_config.target_model, 0)
        target_client = ClientLangChain(app_config.target_provider, **target_kwargs)
    except (ImportError, ValidationError) as e:
        logger.warning(f"Error accessing the Target LLM provider {app_config.target_provider} with model '{app_config.target_model}': {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return
    client_config = ClientConfig(target_client, [target_system_prompt], custom_benchmark=custom_benchmark)

    try:
        attack_kwargs = _build_client_kwargs(app_config, app_config.attack_provider, app_config.attack_model, app_config.attack_temperature)
        attack_config = AttackConfig(
            attack_client = ClientLangChain(app_config.attack_provider, **attack_kwargs),
            attack_prompts_count = app_config.num_attempts,
            embedding_config = _build_embedding_config(app_config)
        )
    except (ImportError, ValidationError) as e:
        logger.warning(f"Error accessing the Attack LLM provider {app_config.attack_provider} with model '{app_config.attack_model}': {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return

    # Run the fuzzer
    fuzz_prompt_injections(client_config, attack_config, threads_count=app_config.num_threads, custom_tests=app_config.tests)
