import os, sys
sys.path.append(os.path.abspath('.'))
import types
from unittest.mock import patch
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.messages import AIMessage
from ps_fuzz.langchain_integration import get_langchain_chat_models_info


def test_get_langchain_chat_models_info_returns_non_empty():
    models = get_langchain_chat_models_info()
    assert models, "expected at least one chat model to be discovered from langchain_community.chat_models"


def test_get_langchain_chat_models_info_resolves_lazy_getattr_exports():
    class FakeModel(BaseChatModel):
        @property
        def _llm_type(self) -> str:
            return "fake_model"

        def _generate(self, messages, **kwargs) -> ChatResult:
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content="ok"))])

    fake_module = types.ModuleType("fake_chat_models_module")
    fake_module.__all__ = ["FakeModel"]

    def __getattr__(name):
        if name == "FakeModel":
            return FakeModel
        raise AttributeError(name)

    fake_module.__getattr__ = __getattr__

    with patch("ps_fuzz.langchain_integration.chat_models_module", fake_module):
        models = get_langchain_chat_models_info()

    assert "fake_model" in models
    assert models["fake_model"].model_cls is FakeModel
