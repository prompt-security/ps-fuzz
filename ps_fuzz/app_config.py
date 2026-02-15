import argparse
import json
import sys, os
import colorama
import pandas as pd
from .util import wrap_text
from .results_table import print_table
import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False

class AppConfig:
    default_config = {
        'attack_provider': 'open_ai',
        'attack_model': 'gpt-3.5-turbo',
        'target_provider': 'open_ai',
        'target_model': 'gpt-3.5-turbo',
        'num_attempts': 3,
        'num_threads': 4,
        'attack_temperature': 0.6,
        'system_prompt': '',
        'custom_benchmark': '',
        'tests': []
    }

    def __init__(self, config_state_file: str, config_state: dict = None):
        if config_state:
            self.config_state = config_state
        else:
            self.config_state_file = config_state_file
            try:
                self.load()
            except Exception as e:
                logger.warning(f"Failed to load config state file {self.config_state_file}: {e}")

    def get_attributes(self):
        attributes = self.config_state.copy()
        return attributes

    def print_as_table(self):
        attributes = self.get_attributes()
        print_table(
            title = "Current configuration",
            headers = ["Option", "Value"],
            data = [[key, value] for key, value in attributes.items() if key != "system_prompt"] # print all except the system prompt
        )
        print(f"{colorama.Style.BRIGHT}Current system prompt:{colorama.Style.RESET_ALL}")
        #print(f"{colorama.Style.DIM}{wrap_text(self.system_prompt, width=70)}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Style.DIM}{self.system_prompt}{colorama.Style.RESET_ALL}")

    def load(self):
        if os.path.exists(self.config_state_file):
            try:
                with open(self.config_state_file, 'r') as f:
                    self.config_state = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {self.config_state_file}: {e}")
                self.config_state = self.default_config.copy()
                self.save()  # Save defaults if existing config is corrupt
            except IOError as e:
                logger.error(f"IO error when opening {self.config_state_file}: {e}")
        else:
            self.config_state = self.default_config.copy()
            self.save()

    def save(self):
        with open(self.config_state_file, 'w') as f:
            json.dump(self.config_state, f, indent=4)

    @property
    def attack_provider(self) -> str:
        return self.config_state['attack_provider']

    @attack_provider.setter
    def attack_provider(self, value: str):
        if not value: raise ValueError("Attack provider cannot be empty")
        self.config_state['attack_provider'] = value
        self.save()

    @property
    def attack_model(self) -> str:
        return self.config_state['attack_model']

    @attack_model.setter
    def attack_model(self, value: str):
        if not value: raise ValueError("Attack model cannot be empty")
        self.config_state['attack_model'] = value
        self.save()

    @property
    def attack_temperature(self) -> float:
        return self.config_state['attack_temperature']

    @attack_temperature.setter
    def attack_temperature(self, value: float):
        if not (0.0 <= value <= 1.0): raise ValueError("Attack temperature must be between 0.0 and 1.0")
        self.config_state['attack_temperature'] = value
        self.save()

    @property
    def target_provider(self) -> str:
        return self.config_state['target_provider']

    @target_provider.setter
    def target_provider(self, value: str):
        if not value: raise ValueError("Target provider cannot be empty")
        self.config_state['target_provider'] = value
        self.save()

    @property
    def target_model(self) -> str:
        return self.config_state['target_model']

    @target_model.setter
    def target_model(self, value: str):
        if not value: raise ValueError("Target model cannot be empty")
        self.config_state['target_model'] = value
        self.save()

    @property
    def custom_benchmark(self) -> str:
        return self.config_state['custom_benchmark']

    @custom_benchmark.setter
    def custom_benchmark(self, value: str):
        if not value: #raise ValueError("Custom benchmark file cannot be empty, has to be a path to file")
            self.config_state['custom_benchmark'] = value
            self.save()
            return
        if not os.path.exists(value): raise ValueError("Custom benchmark file does not exist")
        if not os.path.isfile(value): raise ValueError("Custom benchmark file is not a file")
        if not os.access(value, os.R_OK): raise ValueError("Custom benchmark file is not readable")
        if os.path.getsize(value) == 0: raise ValueError("Custom benchmark file is empty")
        if not value.endswith('.csv'): raise ValueError("Custom benchmark file must be a CSV file")
        df = pd.read_csv(value)
        if 'prompt' not in df.columns: raise ValueError("Custom benchmark file must have a 'prompt' column")
        if 'response' not in df.columns: raise ValueError("Custom benchmark file must have a 'response' column")
        self.config_state['custom_benchmark'] = value
        self.save()

    @property
    def tests(self) -> [str]:
        return self.config_state['tests']

    @tests.setter
    def tests(self, value: str):
        try:
            if len(value) > 0:
                self.config_state['tests'] = json.loads(value)
            else:
                self.config_state['tests'] = []
        except Exception as e:
            self.config_state['tests'] = []
        self.save()

    @property
    def num_attempts(self) -> int:
        return self.config_state['num_attempts']

    @num_attempts.setter
    def num_attempts(self, value: int):
        if value < 1: raise ValueError("Number of attempts must be at least 1")
        self.config_state['num_attempts'] = value
        self.save()

    @property
    def num_threads(self) -> int:
        return self.config_state['num_threads']

    @num_threads.setter
    def num_threads(self, value: int):
        if value < 1: raise ValueError("Number of threads must be at least 1")
        self.config_state['num_threads'] = value
        self.save()

    @property
    def system_prompt(self) -> str:
        return self.config_state['system_prompt']

    @system_prompt.setter
    def system_prompt(self, value: str):
        self.config_state['system_prompt'] = value
        self.save()
        
    @property
    def ollama_base_url(self) -> str:
        return self.config_state.get('ollama_base_url', '')
    
    @ollama_base_url.setter
    def ollama_base_url(self, value: str):
        self.config_state['ollama_base_url'] = value
        self.save()
        
    @property
    def openai_base_url(self) -> str:
        return self.config_state.get('openai_base_url', '')
    
    @openai_base_url.setter
    def openai_base_url(self, value: str):
        self.config_state['openai_base_url'] = value
        self.save()
        
    @property
    def embedding_provider(self) -> str:
        return self.config_state.get('embedding_provider', '')
    
    @embedding_provider.setter
    def embedding_provider(self, value: str):
        self.config_state['embedding_provider'] = value if value else ''
        self.save()
        
    @property
    def embedding_ollama_base_url(self) -> str:
        return self.config_state.get('embedding_ollama_base_url', '')
    
    @embedding_ollama_base_url.setter
    def embedding_ollama_base_url(self, value: str):
        self.config_state['embedding_ollama_base_url'] = value
        self.save()
        
    @property
    def embedding_openai_base_url(self) -> str:
        return self.config_state.get('embedding_openai_base_url', '')
    
    @embedding_openai_base_url.setter
    def embedding_openai_base_url(self, value: str):
        self.config_state['embedding_openai_base_url'] = value
        self.save()
        
    @property
    def embedding_model(self) -> str:
        return self.config_state.get('embedding_model', '')
    
    @embedding_model.setter
    def embedding_model(self, value: str):
        self.config_state['embedding_model'] = value if value else ''
        self.save()

    def update_from_args(self, args):
        args_dict = vars(args)
        for key, value in args_dict.items():
            if value is None: continue
            try:
                if key == 'system_prompt_file':
                    with (sys.stdin if value == "-" else open(value, "r")) as f:
                        self.system_prompt = f.read()
                else:
                    setattr(self, key, value)
            except AttributeError:
                logger.warning(f"Attempt to set an undefined configuration property '{key}'")
                raise
            except Exception as e:
                logger.error(f"Error setting {key}: {e}")
                raise
        self.save()

def parse_cmdline_args():
    parser = argparse.ArgumentParser(description='Prompt Security LLM Prompt Injection Fuzzer')
    parser.add_argument('--list-providers', action='store_true', help="List available providers and exit")
    parser.add_argument('--list-attacks', action='store_true', help="List available attacks and exit")
    parser.add_argument('--attack-provider', type=str, default=None, help="Attack provider")
    parser.add_argument('--attack-model', type=str, default=None, help="Attack model")
    parser.add_argument('--target-provider', type=str, default=None, help="Target provider")
    parser.add_argument('--target-model', type=str, default=None, help="Target model")
    parser.add_argument('--custom-benchmark', type=str, default='', help="Custom benchmark file")
    parser.add_argument('--tests', type=str, default='', help="Custom test configuration (LIST)")
    parser.add_argument('-n', '--num-attempts', type=int, default=None, help="Number of different attack prompts")
    parser.add_argument('-t', '--num-threads', type=int, default=None, help="Number of worker threads")
    parser.add_argument('-a', '--attack-temperature', type=float, default=None, help="Temperature for attack model")
    parser.add_argument('-d', '--debug-level', type=int, default=None, help="Debug level (0-2)")
    parser.add_argument("-b", '--batch', action='store_true', help="Run the fuzzer in unattended (batch) mode, bypassing the interactive steps")
    parser.add_argument('--ollama-base-url', type=str, dest='ollama_base_url', default=None, help="Base URL for Ollama API")
    parser.add_argument('--openai-base-url', type=str, dest='openai_base_url', default=None, help="Base URL for OpenAI API")
    parser.add_argument('--embedding-provider', type=str, dest='embedding_provider', default=None, help="Embedding provider (ollama or open_ai)")
    parser.add_argument('--embedding-ollama-base-url', type=str, dest='embedding_ollama_base_url', default=None, help="Base URL for Ollama Embedding API")
    parser.add_argument('--embedding-openai-base-url', type=str, dest='embedding_openai_base_url', default=None, help="Base URL for OpenAI Embedding API")
    parser.add_argument('--embedding-model', type=str, dest='embedding_model', default=None, help="Embedding model name")
    parser.add_argument('system_prompt_file', type=str, nargs='?', default=None, help="Filename containing the system prompt")
    return parser.parse_args()

