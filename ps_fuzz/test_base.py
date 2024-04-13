# Each test is designed to compromise the LLM model's ability to stick to the given system prompt, but in a different way.
# A system prompt is assumed to restrict the model to not talk about certain topics, or to not provide certain information,
# or contrary, to stick to providing specific topic or kind of information.
from .client_config import ClientConfig
from .attack_config import AttackConfig
from typing import Generator, List
from abc import ABC, abstractmethod

class TestLogEntry(object):
    "A single test step log entry"
    def __init__(self, prompt: str, response: str, success: bool, additional_info: str):
        self.prompt = prompt # The prompt sent to the LLM model
        self.response = response # The response from the LLM model
        self.success = success # True if the attack was successful (this means system prompt was weak), False otherwise
        self.additional_info = additional_info

    def __str__(self):
        return f"TestLog(prompt={self.prompt}, response={self.response}, success={self.success}, additional_info='{self.additional_info})'"

class TestStatus(object):
    """
    Keeps track of the successful and failed prompts, as well as the log of all interactions with the target LLM model.
    """
    def __init__(self):
        self.breach_count: int = 0
        self.resilient_count: int = 0
        self.error_count: int = 0
        self.total_count: int = 0
        self.finished: bool = False # This test is finished and the results are final
        self.log: List[TestLogEntry] = []

    def __str__(self):
        return f"TestStatus(breach_count={self.breach_count}, resilient_count={self.resilient_count}, total_count={self.total_count}, log:{len(self.log)} entries)"

    def report_breach(self, prompt: str, response: str, additional_info: str = "Attack succesfully broke system prompt protection"):
        "Reports a succesful breach of the system prompt"
        self.breach_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, response, True, additional_info))

    def report_resilient(self, prompt: str, response: str, additional_info: str = "Attack failed to break system prompt protection"):
        "Reports a failed attack, meaning the system prompt was resilient"
        self.resilient_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, response, False, additional_info))

    def report_error(self, prompt: str, additional_info: str = "Error"):
        "Reports an error during the test"
        self.error_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, None, False, additional_info))

class StatusUpdate:
    "Represents a status update during the execution of a test"
    def __init__(self, client_config: ClientConfig, test_name: str, status: TestStatus, action: str, progress_position: int, progress_total: int):
        self.test_name = test_name
        self.client_config: ClientConfig = client_config
        self.status: TestStatus = status
        self.action: str = action
        self.progress_position: int = progress_position
        self.progress_total: int = progress_total

class TestBase(ABC):
    """
    A base class for test classes. Each test represents a different kind of attack against the target LLM model.
    The test sends a sequence of prompts and evaluate the responses while updating the status.
    """
    def __init__(self, client_config: ClientConfig, attack_config: AttackConfig, test_name: str, test_description: str):
        self.test_name = test_name
        self.test_description = test_description
        self.client_config = client_config
        self.attack_config = attack_config
        self.status = TestStatus()

    @abstractmethod
    def run(self) -> Generator[StatusUpdate, None, None]:
        """
        An abstract method to be implemented by subclasses to run the test.
        This method is iterable. It yields StatusUpdate objects to report progress.
        """
        pass
