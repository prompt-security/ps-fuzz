from .chat_clients import ClientBase, ChatSession
from typing import List

def summarize_system_prompts(client: ClientBase, system_prompts: List[str]) -> str:
    "Given list of system prompts, summarize them and return a short (up to 5 words) representation of the idea behind them"
    chat = ChatSession(client)
    separator = "----------------------------------"
    user_message = f"""
    There is an LLM system which have the following system prompts. Based on this information,
    can you summarize it's context single sentence? Use the following format: verb + noun. Use maximum 5 words.
    Here are the system prompts:
    {separator}
    {separator.join(system_prompts)}
    {separator}
    """
    return chat.say(user_message)

class ClientConfig(object):
    def __init__(self, target_client: ClientBase, target_system_prompts: List[str], custom_benchmark: str = None):
        self.target_client = target_client
        self.system_prompts = target_system_prompts
        self.system_prompts_summary = None
        self.custom_benchmark = custom_benchmark

    def get_target_client(self):
        return self.target_client

    def get_system_prompts(self):
        return self.system_prompts

    def get_system_prompts_summary(self, attack_client: ClientBase) -> str:
        if self.system_prompts_summary == None:
            # Only compute summary once (lazy, on first call)
            self.system_prompts_summary = summarize_system_prompts(attack_client, self.system_prompts)
        return self.system_prompts_summary
