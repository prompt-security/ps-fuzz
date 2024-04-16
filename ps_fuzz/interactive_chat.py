from .chat_clients import *
import colorama
# Use prompt_toolkit's ability to present a working text editor
from prompt_toolkit import prompt as prompt_toolkit_prompt, HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
import logging
logger = logging.getLogger(__name__)

def text_input(prompt_text:str, initial_text: str = "") -> str:
    bindings = KeyBindings()

    @bindings.add('c-m') # enter key
    def _(event):
        event.app.exit(result=event.app.current_buffer.text)

    # Prompt for input using the session
    try:
        return prompt_toolkit_prompt(
            HTML("<prompt>" + prompt_text + "</prompt>"),
            default=initial_text,
            multiline=False,
            key_bindings=bindings,
            style=Style.from_dict({
                'prompt':  'fg:orange',
            }),
        )
    except KeyboardInterrupt:
        print(f"{colorama.Fore.RED}Edit cancelled by user.{colorama.Style.RESET_ALL}")
        return initial_text

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT
BRIGHT_BLUE = colorama.Fore.BLUE + colorama.Style.BRIGHT
BRIGHT_RED = colorama.Fore.RED + colorama.Style.BRIGHT
BRIGHT_ORANGE = colorama.Fore.YELLOW + colorama.Style.BRIGHT

def interactive_chat(client: ClientBase, system_prompts:List[str] = None):
    "Interactive chat session with optional system prompt. To be used for debugging and manual testing of system prompts"
    chat = ChatSession(client, system_prompts)
    print(f"{BRIGHT}Interactive chat with your system prompt. This emulates a chat session against your LLM-powered chat application. You can try different attacks here.{RESET}")
    print(f"You can chat now. Empty input ends the session.")
    while True:
        user_prompt = text_input(f"You> ")
        if user_prompt == "": break
        response = chat.say(user_prompt)
        if response:
            print(f"{BRIGHT_ORANGE}AI{RESET}> {response}")
