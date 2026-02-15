import os, sys
sys.path.append(os.path.abspath('.'))
from unittest.mock import patch, MagicMock
from ps_fuzz.chat_clients import ClientBase, ClientLangChain, MessageList, BaseMessage, SystemMessage, HumanMessage, AIMessage
from ps_fuzz.langchain_integration import ChatModelParams, ChatModelInfo
from ps_fuzz.attack_config import AttackConfig
from ps_fuzz.client_config import ClientConfig
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


class TestClientLangChainBaseURL:
    """Test class for ClientLangChain base URL parameter transformation."""
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_ollama_base_url_parameter_transformation(self):
        """Test ollama_base_url → base_url transformation."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        # Update fake_chat_models_info to use our mock
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['ollama'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test ollama provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client with ollama_base_url parameter
            ClientLangChain(
                backend='ollama',
                model='llama2',
                temperature=0.7,
                ollama_base_url='http://localhost:11434'
            )
            
            # Verify the model was called with base_url instead of ollama_base_url
            mock_model_cls.assert_called_once_with(
                model='llama2',
                temperature=0.7,
                base_url='http://localhost:11434'
            )
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_openai_base_url_parameter_transformation(self):
        """Test openai_base_url → base_url transformation."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        # Update fake_chat_models_info to use our mock
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['open_ai'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test openai provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client with openai_base_url parameter
            ClientLangChain(
                backend='open_ai',
                model='gpt-3.5-turbo',
                temperature=0.5,
                openai_base_url='https://api.openai.com/v1'
            )

            # Verify the model was called with base_url instead of openai_base_url
            mock_model_cls.assert_called_once_with(
                model='gpt-3.5-turbo',
                temperature=0.5,
                base_url='https://api.openai.com/v1'
            )
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_base_url_parameter_removal(self):
        """Test original parameter is removed from kwargs."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        # Test ollama parameter removal
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['ollama'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test ollama provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            ClientLangChain(
                backend='ollama',
                model='llama2',
                ollama_base_url='http://localhost:11434'
            )

            # Verify ollama_base_url was not passed to the model constructor
            call_args = mock_model_cls.call_args
            assert 'ollama_base_url' not in call_args.kwargs
            assert 'base_url' in call_args.kwargs
            assert call_args.kwargs['base_url'] == 'http://localhost:11434'

        # Reset mock for openai test
        mock_model_cls.reset_mock()

        # Test openai parameter removal
        test_chat_models_info['open_ai'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test openai provider",
            params={}
        )

        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            ClientLangChain(
                backend='open_ai',
                model='gpt-3.5-turbo',
                openai_base_url='https://api.openai.com/v1'
            )
            
            # Verify openai_base_url was not passed to the model constructor
            call_args = mock_model_cls.call_args
            assert 'openai_base_url' not in call_args.kwargs
            assert 'base_url' in call_args.kwargs
            assert call_args.kwargs['base_url'] == 'https://api.openai.com/v1'
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_no_base_url_parameters(self):
        """Test normal operation without base URL parameters."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['ollama'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test ollama provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client without base URL parameters
            ClientLangChain(
                backend='ollama',
                model='llama2',
                temperature=0.7
            )

            # Verify no base_url parameter was added
            call_args = mock_model_cls.call_args
            assert 'base_url' not in call_args.kwargs
            assert 'ollama_base_url' not in call_args.kwargs
            assert call_args.kwargs['model'] == 'llama2'
            assert call_args.kwargs['temperature'] == 0.7
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_empty_base_url_parameters(self):
        """Test behavior with empty base URL values."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['ollama'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test ollama provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client with empty ollama_base_url
            ClientLangChain(
                backend='ollama',
                model='llama2',
                temperature=0.7,
                ollama_base_url=''
            )

            # Verify empty base URL parameters are filtered out
            call_args = mock_model_cls.call_args
            assert 'base_url' not in call_args.kwargs
            assert 'ollama_base_url' not in call_args.kwargs

        # Reset mock for openai test
        mock_model_cls.reset_mock()

        test_chat_models_info['open_ai'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test openai provider",
            params={}
        )

        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client with empty openai_base_url
            ClientLangChain(
                backend='open_ai',
                model='gpt-3.5-turbo',
                temperature=0.5,
                openai_base_url=''
            )

            # Verify empty base URL parameters are filtered out
            call_args = mock_model_cls.call_args
            assert 'base_url' not in call_args.kwargs
            assert 'openai_base_url' not in call_args.kwargs
    
    @patch('ps_fuzz.chat_clients.chat_models_info', fake_chat_models_info)
    def test_base_url_with_other_parameters(self):
        """Test base URL handling with other client parameters."""
        # Mock the model class to capture constructor arguments
        mock_model_cls = MagicMock()
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        test_chat_models_info = fake_chat_models_info.copy()
        test_chat_models_info['ollama'] = ChatModelInfo(
            model_cls=mock_model_cls,
            doc="Test ollama provider",
            params={}
        )
        
        with patch('ps_fuzz.chat_clients.chat_models_info', test_chat_models_info):
            # Create client with base URL and other parameters
            ClientLangChain(
                backend='ollama',
                model='llama2',
                temperature=0.8,
                ollama_base_url='http://custom-ollama:8080',
                max_tokens=1000,
                top_p=0.9
            )
            
            # Verify all parameters are passed correctly
            call_args = mock_model_cls.call_args
            expected_kwargs = {
                'model': 'llama2',
                'temperature': 0.8,
                'base_url': 'http://custom-ollama:8080',
                'max_tokens': 1000,
                'top_p': 0.9
            }
            assert call_args.kwargs == expected_kwargs
            assert 'ollama_base_url' not in call_args.kwargs


class TestAttackConfigEmbedding:
    """Test class for AttackConfig embedding integration."""
    
    def test_attack_config_with_embedding_config(self):
        """Test AttackConfig creation with embedding_config."""
        # Create mock client config
        mock_client_config = MagicMock(spec=ClientConfig)
        
        # Create embedding config
        embedding_config = {
            'embedding_provider': 'ollama',
            'embedding_model': 'nomic-embed-text',
            'embedding_ollama_base_url': 'http://localhost:11434'
        }
        
        # Create AttackConfig with embedding_config
        attack_config = AttackConfig(
            attack_client=mock_client_config,
            attack_prompts_count=10,
            embedding_config=embedding_config
        )
        
        # Verify properties
        assert attack_config.attack_client == mock_client_config
        assert attack_config.attack_prompts_count == 10
        assert attack_config.embedding_config == embedding_config
    
    def test_attack_config_without_embedding_config(self):
        """Test AttackConfig creation without embedding_config."""
        # Create mock client config
        mock_client_config = MagicMock(spec=ClientConfig)
        
        # Create AttackConfig without embedding_config
        attack_config = AttackConfig(
            attack_client=mock_client_config,
            attack_prompts_count=5
        )
        
        # Verify properties
        assert attack_config.attack_client == mock_client_config
        assert attack_config.attack_prompts_count == 5
        assert attack_config.embedding_config is None
    
    def test_attack_config_embedding_config_property(self):
        """Test embedding_config property access."""
        # Create mock client config
        mock_client_config = MagicMock(spec=ClientConfig)
        
        # Create embedding config
        embedding_config = {
            'embedding_provider': 'open_ai',
            'embedding_model': 'text-embedding-ada-002',
            'embedding_openai_base_url': 'https://api.openai.com/v1'
        }
        
        # Create AttackConfig with embedding_config
        attack_config = AttackConfig(
            attack_client=mock_client_config,
            attack_prompts_count=15,
            embedding_config=embedding_config
        )
        
        # Test property access
        assert attack_config.embedding_config['embedding_provider'] == 'open_ai'
        assert attack_config.embedding_config['embedding_model'] == 'text-embedding-ada-002'
        assert attack_config.embedding_config['embedding_openai_base_url'] == 'https://api.openai.com/v1'
    
    def test_attack_config_embedding_config_none(self):
        """Test behavior when embedding_config is None."""
        # Create mock client config
        mock_client_config = MagicMock(spec=ClientConfig)
        
        # Create AttackConfig with explicit None embedding_config
        attack_config = AttackConfig(
            attack_client=mock_client_config,
            attack_prompts_count=20,
            embedding_config=None
        )
        
        # Verify embedding_config is None
        assert attack_config.embedding_config is None
        
        # Verify other properties are still accessible
        assert attack_config.attack_client == mock_client_config
        assert attack_config.attack_prompts_count == 20
