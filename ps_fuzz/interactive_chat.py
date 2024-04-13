from .chat_clients import *
import colorama

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT
BRIGHT_BLUE = colorama.Fore.BLUE + colorama.Style.BRIGHT
BRIGHT_RED = colorama.Fore.RED + colorama.Style.BRIGHT

def interactive_chat(client: ClientBase, system_prompts:List[str] = None):
    "Interactive chat session with optional system prompt. To be used for debugging and manual testing of system prompts"
    chat = ChatSession(client, system_prompts)
    print(f"{BRIGHT}Interactive chatbot.{RESET}")
    print(f"You can chat now. Empty input ends the session.")
    while True:
        user_prompt = input(f"{BRIGHT_BLUE}>{RESET} ")
        if user_prompt == "": break
        response = chat.say(user_prompt)
        if response:
            print(f"{BRIGHT_RED}assistant{RESET}: {response}")
