#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
import sys
import argparse
import colorama
import logging
from logging.handlers import RotatingFileHandler
from .chat_clients import *
from .client_config import ClientConfig
from .attack_config import AttackConfig
from .prompt_injection_fuzzer import *
from .interactive_chat import *
from .logo import print_logo

# Initialize colorama
colorama.init()

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT

LOG_FILE_PATH = "psfuzz.log"

def setup_logging(logging_level):
    # Create file handler with rotation
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s')
    file_handler.setFormatter(formatter)

    # Configure the root logger to use the file handler
    logging.basicConfig(level=logging_level, format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s', handlers=[file_handler])

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Prompt Security LLM Prompt Injection Fuzzer')
    parser.add_argument('-l', '--list-providers', action='store_true', default=False, help="List available providers and exit")
    parser.add_argument('--attack-provider', type=str, default="open_ai", help="Attack provider (default: 'open_ai')")
    parser.add_argument('--attack-model', type=str, default="gpt-3.5-turbo", help="Attack model (default: 'gpt-3.5-turbo')")
    parser.add_argument('--target-provider', type=str, default="open_ai", help="Target provider (default: 'open_ai')")
    parser.add_argument('--target-model', type=str, default="gpt-3.5-turbo", help="Model (default: 'gpt-3.5-turbo')")
    parser.add_argument('-n', '--num-attempts', type=int, default=3, help="Number of different attack prompts to generate for each test (default=3)")
    parser.add_argument('-t', '--num-threads', type=int, default=4, help="Number of worker threads to parallelize the work (default=1)")
    parser.add_argument('-a', '--attack-temperature', type=float, default=0.6, help="Temperature for attack model (default=0.3)")
    parser.add_argument('-d', '--debug-level', type=int, default=1, help="Debug level: 0=only see warnings and errors, 1=info (default), 2=debug/trace")
    parser.add_argument("-i", '--interactive-chat', action='store_true', default=False, help="Run interactive chat instead of the fuzzer. This allows you to chat with the chatbot manually, with the given system prompt in place")
    parser.add_argument('system_prompt_file', type=str, nargs='?', help="Filename containing the system prompt. A special value of '-' means read from stdin.")

    args = parser.parse_args()

    if args.list_providers:
        print("Available providers:")
        for provider_name, provider_info in get_langchain_chat_models_info().items():
            doc = provider_info.doc
            short_doc = doc[:doc.find('\n')]
            print(f"  {BRIGHT}{provider_name}{RESET}: {short_doc}")
        sys.exit(0)

    if args.system_prompt_file is None:
        print(f"Error: You must specify the name of a text file containing your system prompt.\n", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if args.debug_level < 0 and args.debug_level > 2:
        print(f"ERROR: Debug level must be integer between 0-2\n", file=sys.stderr)
        sys.exit(1)

    try:
        target_system_prompt = sys.stdin.read() if args.system_prompt_file == "-" else open(args.system_prompt_file, "r").read()
    except Exception as e:
        print(f"Failed to read system prompt: {e}", file=sys.stderr)
        sys.exit(1)

    # Set up logging
    allowed_logging_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging_level = allowed_logging_levels[args.debug_level]
    setup_logging(logging_level)

    print_logo()

    target_client = ClientLangChain(args.target_provider, model=args.target_model, temperature=0)
    if args.interactive_chat:
        interactive_chat(client=target_client, system_prompts=[target_system_prompt])
    else:
        client_config = ClientConfig(target_client, [target_system_prompt])
        attack_config = AttackConfig(
            attack_client = ClientLangChain(args.attack_provider, model=args.attack_model, temperature=args.attack_temperature),
            attack_prompts_count = args.num_attempts
        )
        # Run the fuzzer
        fuzz_prompt_injections(client_config, attack_config, threads_count=args.num_threads)

if __name__ == "__main__":
    main()
