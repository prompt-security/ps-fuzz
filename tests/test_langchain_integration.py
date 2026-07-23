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
    # get_langchain_chat_models_info() must resolve chat model classes via
    # getattr(), not module.__dict__: langchain_community.chat_models exports its
    # classes lazily, listing 63 names in __all__ but only resolving each one
    # through a module-level __getattr__ (PEP 562) -- they're never stored in the
    # module's __dict__. Reading __dict__ directly would silently resolve every
    # class to None. This test reproduces that lazy-export mechanism with a
    # minimal fake module, independent of langchain_community's actual
    # (changeable) internals.
    class FakeModel(BaseChatModel):
        @property
        def _llm_type(self) -> str:
            return "fake_model"

        def _generate(self, messages, **kwargs) -> ChatResult:
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content="ok"))])

    fake_module = types.ModuleType("fake_chat_models_module")
    # get_langchain_chat_models_info() loops over __all__ to know which names to
    # look up -- it's just candidate names, not a way to access them directly.
    fake_module.__all__ = ["FakeModel"]

    # FakeModel is deliberately never placed in fake_module.__dict__, only reachable
    # via __getattr__ -- this is what makes fake_module.__dict__.get("FakeModel")
    # return None while getattr(fake_module, "FakeModel", None) resolves it.
    def __getattr__(name):
        if name == "FakeModel":
            return FakeModel
        raise AttributeError(name)

    fake_module.__getattr__ = __getattr__

    # Patch by usage site (ps_fuzz.langchain_integration.chat_models_module), not
    # definition site (langchain_community.chat_models) -- patch() replaces the name
    # as looked up inside langchain_integration.py, without touching the real library
    # for any other consumer. Restored automatically once the `with` block exits.
    with patch("ps_fuzz.langchain_integration.chat_models_module", fake_module):
        models = get_langchain_chat_models_info()

    assert len(models) == 1
    assert "fake_model" in models
    assert models["fake_model"].model_cls is FakeModel
