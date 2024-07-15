from ..chat_clients import ChatSession
from ..client_config import ClientConfig
from ..attack_config import AttackConfig
from ..test_base import TestBase, StatusUpdate
from ..attack_registry import register_test
from ..util import contains_refusal_keywords
from .utils import evaluate_response
from typing import Generator
import pandas as pd
import os
from pkg_resources import resource_filename # for loading attack data file packaged with the library
import logging
logger = logging.getLogger(__name__)

@register_test
class CustomBenchmarkTest(TestBase):
    def __init__(self, client_config: ClientConfig, attack_config: AttackConfig):
        super().__init__(
            client_config,
            attack_config,
            test_name = "custom_benchmark_test",
            test_description = "Challenge the LLM with a dataset of prompt injections given by the user"
        )

    def run(self)  -> Generator[StatusUpdate, None, None]:
        if isinstance(self.client_config.custom_benchmark,pd.DataFrame):
            data = self.client_config.custom_benchmark
        else:
            dataset_filename = self.client_config.custom_benchmark
            if dataset_filename is None or not os.path.exists(dataset_filename):
                yield StatusUpdate(self.client_config, self.test_name,
                                   self.status,"N/A", 1, 1)
                return
            data = pd.read_csv(dataset_filename)
        rows_count = data.shape[0]

        if rows_count > self.attack_config.attack_prompts_count:
            # If dataset is larger than requested number of attack samples, reduce dataset by taking attack_prompts_count samples
            data = data.sample(n=self.attack_config.attack_prompts_count, random_state=42)  # constant `random_state` for better reproducibility
            rows_count = data.shape[0]

        # Generate list of attack prompt variations
        yield StatusUpdate(self.client_config, self.test_name, self.status, "Working", 0, rows_count)
        chat = ChatSession(self.client_config.get_target_client(), self.client_config.get_system_prompts())
        for attack_prompt_index, row in data.iterrows():
            try:
                attack_prompt = row['prompt']
            except Exception as e:
                logger.error(f"Error while reading attack prompt from dataset: {e}")
                self.status.report_error(attack_prompt)

            response = chat.say(attack_prompt)
            if not response:
                logger.warning("Error while attacking against target LLM (didn't receive response) ...")
                self.status.report_error(attack_prompt)

            # This is a simple way to discriminate refusal from compliance without requiring a full NLP model.
            # verified = not contains_refusal_keywords(response)
            # The idea is to check that response contains something similar to expected response, but without refusal keywords
            correct_response = evaluate_response(self.attack_config.attack_client,response,row['response']) and not contains_refusal_keywords(response)
            logger.info(f"Test '{self.test_name}': attack prompt #{attack_prompt_index}: {attack_prompt}")
            logger.info(f"Test '{self.test_name}': attack response #{attack_prompt_index} break_success={correct_response}): {response}")

            if not correct_response:
                self.status.report_breach(attack_prompt, response)
            else:
                self.status.report_resilient(attack_prompt, response)
            yield StatusUpdate(self.client_config, self.test_name, self.status, "Attacking", attack_prompt_index, self.attack_config.attack_prompts_count)
        yield StatusUpdate(self.client_config, self.test_name, self.status, "Completed", rows_count, rows_count)
