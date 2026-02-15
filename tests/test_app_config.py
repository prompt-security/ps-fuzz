import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
from ps_fuzz.app_config import AppConfig


class TestAppConfigEmbeddingProperties:
    """Test class for AppConfig embedding-related properties."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    @pytest.fixture
    def mock_config_data(self):
        """Mock configuration data for testing."""
        return {
            'attack_provider': 'open_ai',
            'attack_model': 'gpt-3.5-turbo',
            'target_provider': 'open_ai',
            'target_model': 'gpt-3.5-turbo',
            'num_attempts': 3,
            'num_threads': 4,
            'attack_temperature': 0.6,
            'system_prompt': '',
            'custom_benchmark': '',
            'tests': [],
            'embedding_provider': 'ollama',
            'embedding_model': 'nomic-embed-text',
            'embedding_ollama_base_url': 'http://localhost:11434',
            'embedding_openai_base_url': 'https://api.openai.com/v1'
        }

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_provider_getter_setter_valid(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test valid embedding providers ('ollama', 'open_ai')."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_provider': 'ollama'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.embedding_provider == 'ollama'

        # Test setter with valid values
        config.embedding_provider = 'open_ai'
        assert config.config_state['embedding_provider'] == 'open_ai'
        mock_json_dump.assert_called()

        config.embedding_provider = 'ollama'
        assert config.config_state['embedding_provider'] == 'ollama'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_provider_setter_empty_allowed(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test that empty embedding provider is accepted (consistent with getter default)."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_provider': 'ollama'}

        config = AppConfig('test_config.json')

        config.embedding_provider = ''
        assert config.config_state['embedding_provider'] == ''

        config.embedding_provider = None
        assert config.config_state['embedding_provider'] == ''

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_model_getter_setter_valid(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test valid embedding model names."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_model': 'nomic-embed-text'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.embedding_model == 'nomic-embed-text'

        # Test setter with valid values
        config.embedding_model = 'text-embedding-ada-002'
        assert config.config_state['embedding_model'] == 'text-embedding-ada-002'
        mock_json_dump.assert_called()

        config.embedding_model = 'all-MiniLM-L6-v2'
        assert config.config_state['embedding_model'] == 'all-MiniLM-L6-v2'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_model_setter_empty_allowed(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test that empty embedding model is accepted (consistent with getter default)."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_model': 'nomic-embed-text'}

        config = AppConfig('test_config.json')

        config.embedding_model = ''
        assert config.config_state['embedding_model'] == ''

        config.embedding_model = None
        assert config.config_state['embedding_model'] == ''

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_ollama_base_url_getter_setter(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test embedding Ollama base URL setting/getting (allows empty)."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_ollama_base_url': 'http://localhost:11434'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.embedding_ollama_base_url == 'http://localhost:11434'

        # Test setter with valid URL
        config.embedding_ollama_base_url = 'http://custom-ollama:8080'
        assert config.config_state['embedding_ollama_base_url'] == 'http://custom-ollama:8080'
        mock_json_dump.assert_called()

        # Test setter with empty value (should be allowed)
        config.embedding_ollama_base_url = ''
        assert config.config_state['embedding_ollama_base_url'] == ''

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_openai_base_url_getter_setter(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test embedding OpenAI base URL setting/getting (allows empty)."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'embedding_openai_base_url': 'https://api.openai.com/v1'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.embedding_openai_base_url == 'https://api.openai.com/v1'

        # Test setter with valid URL
        config.embedding_openai_base_url = 'https://custom-openai.example.com/v1'
        assert config.config_state['embedding_openai_base_url'] == 'https://custom-openai.example.com/v1'
        mock_json_dump.assert_called()

        # Test setter with empty value (should be allowed)
        config.embedding_openai_base_url = ''
        assert config.config_state['embedding_openai_base_url'] == ''

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_properties_persistence(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test embedding properties config save/load cycle."""
        mock_exists.return_value = True
        initial_config = {
            'embedding_provider': 'ollama',
            'embedding_model': 'nomic-embed-text',
            'embedding_ollama_base_url': 'http://localhost:11434',
            'embedding_openai_base_url': ''
        }
        mock_json_load.return_value = initial_config

        config = AppConfig('test_config.json')

        # Modify properties
        config.embedding_provider = 'open_ai'
        config.embedding_model = 'text-embedding-ada-002'
        config.embedding_ollama_base_url = ''
        config.embedding_openai_base_url = 'https://api.openai.com/v1'

        # Verify save was called for each property change
        assert mock_json_dump.call_count == 4

        # Verify final state
        assert config.config_state['embedding_provider'] == 'open_ai'
        assert config.config_state['embedding_model'] == 'text-embedding-ada-002'
        assert config.config_state['embedding_ollama_base_url'] == ''
        assert config.config_state['embedding_openai_base_url'] == 'https://api.openai.com/v1'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_embedding_properties_defaults(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test embedding properties default empty values."""
        mock_exists.return_value = True
        mock_json_load.return_value = {}  # Empty config

        config = AppConfig('test_config.json')

        # Test default values (should be empty strings)
        assert config.embedding_provider == ''
        assert config.embedding_model == ''
        assert config.embedding_ollama_base_url == ''
        assert config.embedding_openai_base_url == ''


class TestAppConfigBaseURLProperties:
    """Test class for AppConfig base URL properties."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    @pytest.fixture
    def mock_config_data(self):
        """Mock configuration data for testing."""
        return {
            'attack_provider': 'open_ai',
            'attack_model': 'gpt-3.5-turbo',
            'target_provider': 'open_ai',
            'target_model': 'gpt-3.5-turbo',
            'num_attempts': 3,
            'num_threads': 4,
            'attack_temperature': 0.6,
            'system_prompt': '',
            'custom_benchmark': '',
            'tests': [],
            'ollama_base_url': 'http://localhost:11434',
            'openai_base_url': 'https://api.openai.com/v1'
        }

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_ollama_base_url_getter_setter(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test Ollama base URL setting/getting."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'ollama_base_url': 'http://localhost:11434'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.ollama_base_url == 'http://localhost:11434'

        # Test setter with valid URL
        config.ollama_base_url = 'http://custom-ollama:8080'
        assert config.config_state['ollama_base_url'] == 'http://custom-ollama:8080'
        mock_json_dump.assert_called()

        # Test setter with empty value (should be allowed)
        config.ollama_base_url = ''
        assert config.config_state['ollama_base_url'] == ''

        # Test setter with different protocols
        config.ollama_base_url = 'https://secure-ollama.example.com'
        assert config.config_state['ollama_base_url'] == 'https://secure-ollama.example.com'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_openai_base_url_getter_setter(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test OpenAI base URL setting/getting."""
        mock_exists.return_value = True
        mock_json_load.return_value = {'openai_base_url': 'https://api.openai.com/v1'}

        config = AppConfig('test_config.json')

        # Test getter
        assert config.openai_base_url == 'https://api.openai.com/v1'

        # Test setter with valid URL
        config.openai_base_url = 'https://custom-openai.example.com/v1'
        assert config.config_state['openai_base_url'] == 'https://custom-openai.example.com/v1'
        mock_json_dump.assert_called()

        # Test setter with empty value (should be allowed)
        config.openai_base_url = ''
        assert config.config_state['openai_base_url'] == ''

        # Test setter with Azure OpenAI format
        config.openai_base_url = 'https://myresource.openai.azure.com/'
        assert config.config_state['openai_base_url'] == 'https://myresource.openai.azure.com/'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_base_url_properties_persistence(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test base URL properties config save/load cycle."""
        mock_exists.return_value = True
        initial_config = {
            'ollama_base_url': 'http://localhost:11434',
            'openai_base_url': 'https://api.openai.com/v1'
        }
        mock_json_load.return_value = initial_config

        config = AppConfig('test_config.json')

        # Modify properties
        config.ollama_base_url = 'http://custom-ollama:8080'
        config.openai_base_url = 'https://custom-openai.example.com/v1'

        # Verify save was called for each property change
        assert mock_json_dump.call_count == 2

        # Verify final state
        assert config.config_state['ollama_base_url'] == 'http://custom-ollama:8080'
        assert config.config_state['openai_base_url'] == 'https://custom-openai.example.com/v1'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_base_url_properties_defaults(self, mock_exists, mock_json_load, mock_json_dump, mock_file):
        """Test base URL properties default empty values."""
        mock_exists.return_value = True
        mock_json_load.return_value = {}  # Empty config

        config = AppConfig('test_config.json')

        # Test default values (should be empty strings)
        assert config.ollama_base_url == ''
        assert config.openai_base_url == ''

    @pytest.mark.parametrize("url_property,test_urls", [
        ('ollama_base_url', [
            'http://localhost:11434',
            'https://ollama.example.com',
            'http://192.168.1.100:8080',
            'https://secure-ollama.company.com:443'
        ]),
        ('openai_base_url', [
            'https://api.openai.com/v1',
            'https://custom-openai.example.com/v1',
            'https://myresource.openai.azure.com/',
            'http://localhost:8000/v1'
        ])
    ])
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('json.load')
    @patch('os.path.exists')
    def test_base_url_various_formats(self, mock_exists, mock_json_load, mock_json_dump, mock_file, url_property, test_urls):
        """Test base URL properties with various URL formats."""
        mock_exists.return_value = True
        mock_json_load.return_value = {}

        config = AppConfig('test_config.json')

        for url in test_urls:
            setattr(config, url_property, url)
            assert config.config_state[url_property] == url
            assert getattr(config, url_property) == url
