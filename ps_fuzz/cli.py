#!/usr/bin/env python3
import os
import sys
import colorama
from dotenv import load_dotenv
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
from .ps_logging import setup_logging
from .chat_clients import *
from .client_config import ClientConfig
from .attack_config import AttackConfig
from .prompt_injection_fuzzer import *
from .app_config import AppConfig, parse_cmdline_args
from .interactive_mode import interactive_shell
from .prompt_injection_fuzzer import run_fuzzer
from .logo import print_logo
from .util import wrap_text

# Initialize colorama
colorama.init()

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT

# Maintain configuration state in the user's home directory
APP_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".prompt-security-fuzzer-config.json")

def main():
    # Print the logo
    print_logo()

    # Parse command line arguments
    args = parse_cmdline_args()

    # Execute immediate commands
    if args.list_providers:
        print("Available providers:")
        for provider_name, provider_info in get_langchain_chat_models_info().items():
            print(f"  {BRIGHT}{provider_name}{RESET}: {provider_info.short_doc}")
        sys.exit(0)

    if args.list_attacks:
        client_config = ClientConfig(FakeChatClient(), [])
        attack_config = AttackConfig(FakeChatClient(), 1)
        tests = instantiate_tests(client_config, attack_config,[],True)
        print("Available attacks:")
        for test_name, test_description in sorted([(cls.test_name, cls.test_description) for cls in tests]):
            print(f"{BRIGHT}{test_name}{RESET}:\n{wrap_text(test_description)}")
        sys.exit(0)

    # Setup debug level (default 1)
    setup_logging(args.debug_level if args.debug_level is not None else 1)

    # Load application config from file (if exists)
    app_config = AppConfig(config_state_file=APP_CONFIG_FILE)

    # Apply any overrides from command line arguments/options, overriding anything loaded from config file
    app_config.update_from_args(args)

    # Run interactive shell that allows to change configuration or run some tasks
    if args.batch:
        run_fuzzer(app_config)
    else:
        interactive_shell(app_config)
    print(f"{BRIGHT}{colorama.Fore.CYAN}Thank you for trying out the Prompt Security Fuzzer!{RESET}")

if __name__ == "__main__":
    main()
