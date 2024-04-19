from langchain_core.language_models.chat_models import BaseChatModel
import langchain.chat_models
from typing import Any, Dict, get_origin, Optional
import inspect, re

def _get_class_member_doc(cls, param_name: str) -> Optional[str]:
    lines, _ = inspect.getsourcelines(cls)
    state = 0 # 0=waiting, 1=ready, 2=reading mutliline
    doc_lines = []
    for line in lines:
        if state == 0:
            if re.match(f"\\s*({param_name}):", line):
                state = 1
                doc_lines = []
        elif state == 1:
            m = re.match('^\\s*("{1,3})(.*?)("{1,3})?$', line)
            if m:
                m_groups = m.groups()
                if m_groups[2] == m_groups[0]: # closing with the same quotes on the same line
                    doc_lines.append(m_groups[1])
                    return list(doc_lines)
                elif m_groups[0] == '"""': # Opened multi-line
                    doc_lines.append(m_groups[1])
                    state = 2
                else:
                    state = 0 # should not happen (opened with single " and not closed with single " -- this is invalid syntax)
            else:
                state = 0 # no docstring ...
        elif state == 2:
            m = re.match('(.*?)"""$', line)
            if m:
                doc_lines.append(m.group(1))
                return list(doc_lines)
            else:
                doc_lines.append(line)

def camel_to_snake(name):
    "Convert camelCase to snake_case"
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name).lower()

# Global blacklist of Chat Models
EXCLUDED_CHAT_MODELS = [
    'FakeListChatModel',
    'ChatDatabricks',
    'ChatMlflow',
    'HumanInputChatModel'
]

CHAT_MODEL_EXCLUDED_PARAMS = [
    'name',
    'verbose',
    'cache',
    'streaming',
    'tiktoken_model_name',
]

class ChatModelParams(object):
    def __init__(self, typ: Any, default: Any, description: str):
        self.typ = typ
        self.default = default
        self.description = description

    def __str__(self):
        return f"ChatModelParams(typ={self.typ.__name__}, default='{self.default}'{', description=' + chr(39) + self.description + chr(39) if self.description else ''}"

class ChatModelInfo(object):
    def __init__(self, model_cls: BaseChatModel, doc: str, params: Dict[str, Any]):
        self.model_cls = model_cls
        self.doc = doc
        self.params = params

    def __str__(self):
        s = f"ChatModelInfo(model_cls={self.model_cls}:\n"
        for param_name, param in self.params.items():
            if param_name == "doc": continue
            s += f"    {param_name}: {param}\n"
        return s

    @property
    def short_doc(self):
        return self.doc[:self.doc.find('\n')]

def get_langchain_chat_models_info() -> Dict[str, Dict[str, Any]]:
    """
    Introspects a langchain library, extracting information about supported chat models and required/optional parameters
    """
    models: Dict[str, ChatModelInfo] = {}
    for model_cls_name in langchain.chat_models.__all__:
        if model_cls_name in EXCLUDED_CHAT_MODELS: continue
        model_cls = langchain.chat_models.__dict__.get(model_cls_name)
        if model_cls and issubclass(model_cls, BaseChatModel):
            model_short_name = camel_to_snake(model_cls.__name__).replace('_chat', '').replace('chat_', '')
            # Introspect supported model parameters
            params: Dict[str, ChatModelParams] = {}
            for param_name, field in model_cls.__fields__.items():
                if param_name in CHAT_MODEL_EXCLUDED_PARAMS: continue
                typ = field.outer_type_
                if typ not in [str, float, int, bool] and get_origin(typ) not in [str, float, int, bool]: continue
                doc_lines = _get_class_member_doc(model_cls, param_name)
                description = ''.join(doc_lines) if doc_lines else None
                params[param_name] = ChatModelParams(typ=typ, default=field.default, description=description)
            models[model_short_name] = ChatModelInfo(model_cls=model_cls, doc=model_cls.__doc__, params=params)
    return models
