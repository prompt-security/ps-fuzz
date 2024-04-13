import os, sys
sys.path.append(os.path.abspath('.'))
from unittest.mock import patch
from ps_fuzz.chat_clients import ClientBase, ClientLangChain, MessageList, BaseMessage, SystemMessage, HumanMessage, AIMessage
from ps_fuzz.langchain_integration import ChatModelParams, ChatModelInfo
from typing import Dict, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import LLMResult, ChatResult, ChatGeneration
from langchain_core.pydantic_v1 import Field

# Fake LangChain model
class FakeChatModel(BaseChatModel):
    model_name: str = Field(default="fake-model-turbo", alias="model")
    temperature: float = Field(default=5)

    # Implement the very minimum required by BaseChatModel to function
    @property
    def _llm_type(self) -> str:
        return "fake_chat_model"

    def _generate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        response_text= f"fakeresponse: model_name='{self.model_name}'; temperature={self.temperature}; messages_count={len(messages)}"
        generation = ChatGeneration(message=AIMessage(content=response_text), generation_info={"finish_reason": "stop"})
        return ChatResult(generations=[generation])

fake_chat_models_info: Dict[str, ChatModelInfo] = {
    'fake_chat_provider': ChatModelInfo(model_cls=FakeChatModel, doc="Fake chat provider", params={
        'model_name':  ChatModelParams(typ=str, default='default1', description="Fake string param 1"),
        'temperature': ChatModelParams(typ=float, default=0.7, description="Fake temperature"),
    }),
}

@patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
def test_client_langchain():
    client_langchain = ClientLangChain(backend = 'fake_chat_provider', temperature = 0.123)
    fake_history: MessageList = [
        SystemMessage(content = "Fake System Prompt"),
        HumanMessage(content = "Hello"),
    ]
    result = client_langchain.interact(history = fake_history, messages = [])
    assert result == "fakeresponse: model_name='fake-model-turbo'; temperature=0.123; messages_count=2"
