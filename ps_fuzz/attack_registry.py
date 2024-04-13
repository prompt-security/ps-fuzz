from .client_config import ClientConfig
from .attack_config import AttackConfig
from .test_base import TestBase
from typing import List
import logging
logger = logging.getLogger(__name__)

# Attack test classes registry
test_classes = []

# Decorator used to register attack test classes
def register_test(cls):
    "Decorator that registers test types"
    global test_classes
    logger.debug(f"Registering attack test class: {cls.__name__}")
    test_classes.append(cls)

def instantiate_tests(client_config: ClientConfig, attack_config: AttackConfig) -> List[TestBase]:
    tests = []
    for cls in test_classes:
        # TODO: remove ...
        #if test_cls.__name__ != "TestSystemPromptStealer": continue
        logger.debug(f"Instantiating attack test class: {cls.__name__}")
        test_instance = cls(client_config, attack_config)
        tests.append(test_instance)
    return tests
