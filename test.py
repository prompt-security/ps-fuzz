import os
import random
from ps_fuzz.app_config import AppConfig
from ps_fuzz.prompt_injection_fuzzer import run_fuzzer
from ps_fuzz.chat_clients import (
    ClientBase,
    MessageList,
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
import logging
import requests

logger = logging.getLogger(__name__)

APP_CONFIG_FILE = os.path.join(
    os.path.expanduser("~"), ".prompt-security-fuzzer-config.json"
)


class HttpHistoryClient(ClientBase):
    "For custom endpoints that rely on history to be passed by the caller"

    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        history_without_system_prompts = [
            message for message in history if not isinstance(message, SystemMessage)
        ]
        response = requests.post(
            "http://base_endpoint.com/chat",
            json={
                "history": history_without_system_prompts,
                "message": messages[-1].content,
            },
        )

        response_json = response.json()
        response_message = AIMessage(content=response_json["response"])

        # Add messages and response to history, which is weirdly being done by the client wrapper
        history += messages
        history += [response_message]

        return response_message.content


class HttpSessionClient(ClientBase):
    "For custom endpoints that require a chat_id to be maintained between requests"

    def __init__(self):
        try:
            response = requests.post("http://base_endpoint.com/chat")
            response_json = response.json()
            self.chat_id = response_json["chat_id"]
        except Exception as e:
            logger.warning(f"Failed to initialize chat session: {e}")
            raise

    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        last_message = messages[-1]
        if not isinstance(last_message, HumanMessage):
            raise ValueError("Expected last message to be a HumanMessage")

        try:
            response = requests.post(
                f"http://base_endpoint.com/chat/{self.chat_id}",
                json={"message": last_message.content},
            )
            response_json = response.json()
            response_message = AIMessage(content=response_json["response"])
        except Exception as e:
            logger.warning(f"Custom endpoint inference failed with error: {e}")
            raise

        # Add messages and response to history, which is weirdly being done by the client wrapper
        history += messages
        history += [response_message]

        return response_message.content


class StaticClient(ClientBase):
    def __init__(self):
        self.random_number = random.randint(0, 100)

    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        history += messages
        message = f"Here's a random number: {self.random_number}"
        history += [AIMessage(content=message)]
        return message


def custom_chat_endpoint(message: str) -> str:
    return "I'm only talking about finance."


def main():
    # Load application config from file (if exists)
    app_config = AppConfig(config_state_file=APP_CONFIG_FILE)
    app_config.system_prompt = ""
    run_fuzzer(
        app_config,
        target_client_initializer=lambda: StaticClient(),
    )


if __name__ == "__main__":
    main()
