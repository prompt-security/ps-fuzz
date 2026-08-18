from types import SimpleNamespace
from unittest.mock import patch

from ps_fuzz.prompt_injection_fuzzer import run_fuzzer


def test_run_fuzzer_reports_a_missing_optional_provider_integration(caplog):
    """Modern LangChain factory errors should not terminate the interactive run."""
    app_config = SimpleNamespace(
        target_provider='anthropic',
        target_model='claude-test',
        system_prompt='',
        custom_benchmark='',
        print_as_table=lambda: None,
    )

    with patch(
        'ps_fuzz.prompt_injection_fuzzer.ClientLangChain',
        side_effect=ImportError('Install langchain-anthropic'),
    ):
        run_fuzzer(app_config)

    assert 'Error accessing the Target LLM provider anthropic' in caplog.text
