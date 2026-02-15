from .langchain_integration import get_langchain_chat_models_info
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs.llm_result import LLMResult
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import sys
import logging
logger = logging.getLogger(__name__)

# Type representing list of messages (history)
MessageList = List[BaseMessage]

# Introspect langchain for supported models
chat_models_info = get_langchain_chat_models_info()

# Chat clients are defined below
class ClientBase(ABC):
    "Chat model wrappers base"
    @abstractmethod
    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        """Takes history and new message, send to LLM then returns new Message completed by LLM.
           The history is automatically updated during conversation.
        """

class FakeChatClient(ClientBase):
    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        return "FakeChat response"

# Specialized chat client based on langchain supported backends
class ClientLangChain(ClientBase):
    "Chat model wrapper around LangChain"
    def __init__(self, backend: str, **kwargs):
        if backend in chat_models_info:
            model_cls = chat_models_info[backend].model_cls
            
            # Transform provider-specific base_url params to the generic base_url,
            # and remove empty values so they don't get passed to the model constructor.
            if backend == 'ollama' and 'ollama_base_url' in kwargs:
                url = kwargs.pop('ollama_base_url')
                if url:
                    kwargs['base_url'] = url

            if backend == 'open_ai' and 'openai_base_url' in kwargs:
                url = kwargs.pop('openai_base_url')
                if url:
                    kwargs['base_url'] = url
                
            self.client = model_cls(**kwargs)
        else:
            raise ValueError(f"Invalid backend name: {backend}. Supported backends: {', '.join(chat_models_info.keys())}")

    def interact(self, history: MessageList, messages: MessageList) -> BaseMessage:
        # Add prompt messages to the history, send and get completion result from the llm
        history += messages
        try:
            llm_result: LLMResult = self.client.generate(messages = [history])
            response_message: BaseMessage = AIMessage(content = llm_result.generations[0][0].text)
        except Exception as e:
            logger.warning(f"Chat inference failed with error: {e}")
            raise

        # Add response message to the history too
        history += [response_message]
        return response_message.content

# Chat session allows chatting against target client while maintaining state (history buffer)
class ChatSession:
    "Maintains single conversation, including history, and supports an optional system prompts"
    def __init__(self, client: ClientBase, system_prompts: Optional[List[str]] = None):
        self.client = client
        self.system_prompts = None
        if system_prompts:
            self.system_prompts = list(map(lambda system_prompt_text: AIMessage(content=system_prompt_text), system_prompts))
        self.history = []

    def say(self, user_prompt: str):
        logger.debug(f"say: system_prompt={self.system_prompts}")
        logger.debug(f"say: prompt={user_prompt}")
        input_messages = []
        if len(self.history) == 0 and self.system_prompts:
            input_messages.extend(self.system_prompts)
        input_messages.append(HumanMessage(content = user_prompt))
        result = self.client.interact(self.history, input_messages)
        logger.debug(f"say: result={result}")
        return result
