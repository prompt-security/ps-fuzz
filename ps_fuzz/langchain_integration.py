import inspect
import re
import warnings
from typing import Any, Dict, Optional, get_args

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

try:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"`langchain-community` is being sunset.*",
            category=DeprecationWarning,
        )
        import langchain_community.chat_models as chat_models_module
except ImportError:
    chat_models_module = None


def _get_class_member_doc(cls, param_name: str) -> Optional[str]:
    try:
        lines, _ = inspect.getsourcelines(cls)
    except (OSError, TypeError):
        return None

    state = 0  # 0=waiting, 1=ready, 2=reading multiline
    doc_lines = []
    for line in lines:
        if state == 0:
            if re.match(f"\\s*({param_name}):", line):
                state = 1
                doc_lines = []
        elif state == 1:
            match = re.match('^\\s*("{1,3})(.*?)("{1,3})?$', line)
            if match:
                opening, content, closing = match.groups()
                if closing == opening:
                    doc_lines.append(content)
                    return "".join(doc_lines)
                if opening == '"""':
                    doc_lines.append(content)
                    state = 2
                else:
                    state = 0
            else:
                state = 0
        elif state == 2:
            match = re.match('(.*?)"""$', line)
            if match:
                doc_lines.append(match.group(1))
                return "".join(doc_lines)
            doc_lines.append(line)

    return None


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name).lower()


# Chat models that do not represent a provider users can configure.
EXCLUDED_CHAT_MODELS = {
    'FakeListChatModel',
    'ChatDatabricks',
    'ChatMlflow',
    'HumanInputChatModel',
}

CHAT_MODEL_EXCLUDED_PARAMS = {
    'name',
    'verbose',
    'cache',
    'streaming',
    'tiktoken_model_name',
}

# The default install includes these maintained split integrations. The
# ``open_ai`` spelling is retained for existing config files and CLI use.
DEFAULT_CHAT_MODELS = {
    'open_ai': ChatOpenAI,
    'ollama': ChatOllama,
}

# A user who installs another maintained LangChain split integration can keep
# using it through an existing configuration file or CLI invocation. These are
# deliberately not advertised as bundled providers because their integrations
# are optional dependencies.
FACTORY_PROVIDER_ALIASES = {
    'anthropic': 'anthropic',
    'azure_openai': 'azure_openai',
    'bedrock': 'bedrock',
    'cohere': 'cohere',
    'deepseek': 'deepseek',
    'fireworks': 'fireworks',
    'google_genai': 'google_genai',
    'google_vertexai': 'google_vertexai',
    'groq': 'groq',
    'huggingface': 'huggingface',
    'litellm': 'litellm',
    'mistralai': 'mistralai',
    'ollama': 'ollama',
    'open_ai': 'openai',
    'openai': 'openai',
    'openrouter': 'openrouter',
    'perplexity': 'perplexity',
    'together': 'together',
    'upstage': 'upstage',
    'xai': 'xai',
}


def get_factory_provider(backend: str) -> Optional[str]:
    """Return LangChain's canonical provider name for a configured backend."""
    return FACTORY_PROVIDER_ALIASES.get(backend)


class ChatModelParams(object):
    def __init__(self, typ: Any, default: Any, description: Optional[str]):
        self.typ = typ
        self.default = default
        self.description = description

    def __str__(self):
        type_name = getattr(self.typ, '__name__', str(self.typ))
        description = f", description='{self.description}'" if self.description else ''
        return f"ChatModelParams(typ={type_name}, default='{self.default}'{description})"


class ChatModelInfo(object):
    def __init__(self, model_cls: BaseChatModel, doc: str, params: Dict[str, ChatModelParams]):
        self.model_cls = model_cls
        self.doc = doc or ''
        self.params = params

    def __str__(self):
        lines = [f"ChatModelInfo(model_cls={self.model_cls}:"]
        lines.extend(f"    {param_name}: {param}" for param_name, param in self.params.items())
        return '\n'.join(lines)

    @property
    def short_doc(self):
        return self.doc.split('\n', 1)[0] if self.doc else 'LangChain chat model'


def _scalar_annotation(annotation: Any) -> Optional[type]:
    """Find a scalar type in Pydantic's direct or optional annotations."""
    candidates = (annotation, *get_args(annotation))
    return next((candidate for candidate in candidates if candidate in {str, float, int, bool}), None)


def _chat_model_info(model_cls: type[BaseChatModel]) -> ChatModelInfo:
    params: Dict[str, ChatModelParams] = {}
    fields = getattr(model_cls, 'model_fields', None) or getattr(model_cls, '__fields__', {})
    for param_name, field in fields.items():
        if param_name in CHAT_MODEL_EXCLUDED_PARAMS:
            continue
        annotation = getattr(field, 'annotation', None) or getattr(field, 'outer_type_', None)
        scalar_type = _scalar_annotation(annotation)
        if scalar_type is None:
            continue
        params[param_name] = ChatModelParams(
            typ=scalar_type,
            default=field.default,
            description=_get_class_member_doc(model_cls, param_name),
        )
    return ChatModelInfo(model_cls=model_cls, doc=inspect.getdoc(model_cls) or '', params=params)


def get_langchain_chat_models_info(include_legacy: bool = False) -> Dict[str, ChatModelInfo]:
    """Return bundled providers, optionally including legacy community adapters.

    Community adapters are retained for existing configurations, but many need
    vendor-specific packages that are not part of the default install. They
    are therefore excluded from the providers advertised by the CLI and
    interactive UI.
    """
    models: Dict[str, ChatModelInfo] = {
        model_name: _chat_model_info(model_cls)
        for model_name, model_cls in DEFAULT_CHAT_MODELS.items()
    }

    if include_legacy and chat_models_module is not None:
        for model_cls_name in getattr(chat_models_module, '__all__', []):
            if model_cls_name in EXCLUDED_CHAT_MODELS:
                continue
            try:
                model_cls = getattr(chat_models_module, model_cls_name)
            except (AttributeError, ImportError):
                continue
            if not isinstance(model_cls, type) or not issubclass(model_cls, BaseChatModel):
                continue
            model_short_name = camel_to_snake(model_cls.__name__).replace('_chat', '').replace('chat_', '')
            models.setdefault(model_short_name, _chat_model_info(model_cls))

    return dict(sorted(models.items()))
