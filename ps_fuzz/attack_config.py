from .client_config import ClientConfig

class AttackConfig(object):
    def __init__(self, attack_client: ClientConfig, attack_prompts_count: int):
        self.attack_client = attack_client
        self.attack_prompts_count = attack_prompts_count
