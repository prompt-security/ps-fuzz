import pytest
from unittest.mock import MagicMock
from ps_fuzz.prompt_injection_fuzzer import _build_client_kwargs, _build_embedding_config


class TestHelperFunctions:
    """Test class for helper functions from prompt_injection_fuzzer.py."""

    def test_build_client_kwargs_ollama_with_base_url(self):
        """Test kwargs building for Ollama with base URL."""
        mock_app_config = MagicMock()
        mock_app_config.ollama_base_url = 'http://localhost:11434'

        result = _build_client_kwargs(mock_app_config, 'ollama', 'llama2', 0.7)

        expected = {
            'model': 'llama2',
            'temperature': 0.7,
            'ollama_base_url': 'http://localhost:11434'
        }
        assert result == expected

    def test_build_client_kwargs_ollama_without_base_url(self):
        """Test kwargs building for Ollama without base URL."""
        mock_app_config = MagicMock()
        mock_app_config.ollama_base_url = ''

        result = _build_client_kwargs(mock_app_config, 'ollama', 'llama2', 0.7)

        expected = {
            'model': 'llama2',
            'temperature': 0.7
        }
        assert result == expected

    def test_build_client_kwargs_ollama_missing_attribute(self):
        """Test kwargs building for Ollama when base URL attribute is missing."""
        mock_app_config = MagicMock()
        del mock_app_config.ollama_base_url

        result = _build_client_kwargs(mock_app_config, 'ollama', 'llama2', 0.7)

        expected = {
            'model': 'llama2',
            'temperature': 0.7
        }
        assert result == expected

    def test_build_client_kwargs_openai_with_base_url(self):
        """Test kwargs building for OpenAI with base URL."""
        mock_app_config = MagicMock()
        mock_app_config.openai_base_url = 'https://api.openai.com/v1'

        result = _build_client_kwargs(mock_app_config, 'open_ai', 'gpt-3.5-turbo', 0.5)

        expected = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.5,
            'openai_base_url': 'https://api.openai.com/v1'
        }
        assert result == expected

    def test_build_client_kwargs_openai_without_base_url(self):
        """Test kwargs building for OpenAI without base URL."""
        mock_app_config = MagicMock()
        mock_app_config.openai_base_url = ''

        result = _build_client_kwargs(mock_app_config, 'open_ai', 'gpt-3.5-turbo', 0.5)

        expected = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.5
        }
        assert result == expected

    def test_build_client_kwargs_openai_missing_attribute(self):
        """Test kwargs building for OpenAI when base URL attribute is missing."""
        mock_app_config = MagicMock()
        del mock_app_config.openai_base_url

        result = _build_client_kwargs(mock_app_config, 'open_ai', 'gpt-3.5-turbo', 0.5)

        expected = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.5
        }
        assert result == expected

    def test_build_client_kwargs_other_providers(self):
        """Test kwargs building for other providers."""
        mock_app_config = MagicMock()
        mock_app_config.ollama_base_url = 'http://localhost:11434'
        mock_app_config.openai_base_url = 'https://api.openai.com/v1'

        # Test with anthropic provider (should not include any base URLs)
        result = _build_client_kwargs(mock_app_config, 'anthropic', 'claude-3-sonnet', 0.3)

        expected = {
            'model': 'claude-3-sonnet',
            'temperature': 0.3
        }
        assert result == expected

        # Test with google provider (should not include any base URLs)
        result = _build_client_kwargs(mock_app_config, 'google', 'gemini-pro', 0.8)

        expected = {
            'model': 'gemini-pro',
            'temperature': 0.8
        }
        assert result == expected

    def test_build_embedding_config_complete(self):
        """Test embedding config with all properties."""
        mock_app_config = MagicMock()
        mock_app_config.embedding_provider = 'ollama'
        mock_app_config.embedding_model = 'nomic-embed-text'
        mock_app_config.embedding_ollama_base_url = 'http://localhost:11434'
        mock_app_config.embedding_openai_base_url = 'https://api.openai.com/v1'

        result = _build_embedding_config(mock_app_config)

        expected = {
            'embedding_provider': 'ollama',
            'embedding_model': 'nomic-embed-text',
            'embedding_ollama_base_url': 'http://localhost:11434',
            'embedding_openai_base_url': 'https://api.openai.com/v1'
        }
        assert result == expected

    def test_build_embedding_config_partial(self):
        """Test embedding config with missing properties."""
        mock_app_config = MagicMock()
        mock_app_config.embedding_provider = 'open_ai'
        mock_app_config.embedding_model = 'text-embedding-ada-002'
        del mock_app_config.embedding_ollama_base_url
        del mock_app_config.embedding_openai_base_url

        result = _build_embedding_config(mock_app_config)

        expected = {
            'embedding_provider': 'open_ai',
            'embedding_model': 'text-embedding-ada-002',
            'embedding_ollama_base_url': '',
            'embedding_openai_base_url': ''
        }
        assert result == expected

    def test_build_embedding_config_empty(self):
        """Test embedding config with empty AppConfig."""
        mock_app_config = MagicMock()
        del mock_app_config.embedding_provider
        del mock_app_config.embedding_model
        del mock_app_config.embedding_ollama_base_url
        del mock_app_config.embedding_openai_base_url

        result = _build_embedding_config(mock_app_config)

        expected = {
            'embedding_provider': '',
            'embedding_model': '',
            'embedding_ollama_base_url': '',
            'embedding_openai_base_url': ''
        }
        assert result == expected

    @pytest.mark.parametrize("provider,base_url_attr,base_url_value,expected_key", [
        ('ollama', 'ollama_base_url', 'http://localhost:11434', 'ollama_base_url'),
        ('ollama', 'ollama_base_url', 'http://custom-ollama:8080', 'ollama_base_url'),
        ('open_ai', 'openai_base_url', 'https://api.openai.com/v1', 'openai_base_url'),
        ('open_ai', 'openai_base_url', 'https://custom-openai.example.com/v1', 'openai_base_url'),
    ])
    def test_build_client_kwargs_parametrized(self, provider, base_url_attr, base_url_value, expected_key):
        """Test kwargs building with parametrized provider and base URL combinations."""
        mock_app_config = MagicMock()
        setattr(mock_app_config, base_url_attr, base_url_value)

        result = _build_client_kwargs(mock_app_config, provider, 'test-model', 0.6)

        expected = {
            'model': 'test-model',
            'temperature': 0.6,
            expected_key: base_url_value
        }
        assert result == expected

    @pytest.mark.parametrize("embedding_provider,embedding_model,ollama_url,openai_url", [
        ('ollama', 'nomic-embed-text', 'http://localhost:11434', ''),
        ('open_ai', 'text-embedding-ada-002', '', 'https://api.openai.com/v1'),
        ('ollama', 'all-MiniLM-L6-v2', 'http://custom-ollama:8080', 'https://custom-openai.com/v1'),
        ('', '', '', ''),
    ])
    def test_build_embedding_config_parametrized(self, embedding_provider, embedding_model, ollama_url, openai_url):
        """Test embedding config building with parametrized values."""
        mock_app_config = MagicMock()
        mock_app_config.embedding_provider = embedding_provider
        mock_app_config.embedding_model = embedding_model
        mock_app_config.embedding_ollama_base_url = ollama_url
        mock_app_config.embedding_openai_base_url = openai_url

        result = _build_embedding_config(mock_app_config)

        expected = {
            'embedding_provider': embedding_provider,
            'embedding_model': embedding_model,
            'embedding_ollama_base_url': ollama_url,
            'embedding_openai_base_url': openai_url
        }
        assert result == expected
