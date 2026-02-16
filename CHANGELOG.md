# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.1.0] - 2026-02-16

### Added
- **RAG Poisoning Attack** ("Hidden Parrot Attack") — new fuzzing test that demonstrates how malicious instructions embedded in vector databases can compromise RAG system behavior
  - Supports both Ollama and OpenAI embedding providers
  - Configurable embedding model, provider, and base URLs via interactive menu or config file
  - Automatically creates a poisoned vector database with benign and malicious documents, then tests whether the target LLM follows injected instructions
- Embedding configuration properties in `AppConfig` (`embedding_provider`, `embedding_model`, `embedding_ollama_base_url`, `embedding_openai_base_url`)
- Configurable base URLs for Ollama and OpenAI providers (`ollama_base_url`, `openai_base_url`) with proper parameter transformation in chat clients
- `TestStatus.report_skipped()` method and `skipped_count` tracking for tests that cannot run due to missing configuration or dependencies
- GPT-4o with Canvas system prompt leak example (`system_prompt.examples/`)
- Bandit security scanning workflow (`.github/workflows/bandit.yml`)
- Dedicated test files: `test_app_config.py`, `test_prompt_injection_fuzzer_helpers.py`, `test_test_status.py`

### Security
- **[CRITICAL] CVE-2025-68664** — Upgraded langchain ecosystem (langchain, langchain-core, langchain-community) from 0.0.x to 0.3.x to fix serialization injection vulnerability that could allow secret extraction and arbitrary code execution
- **[HIGH] CVE-2024-34062** — Upgraded tqdm from 4.66.1 to ≥4.66.3 to fix CLI arguments injection via `eval()`
- **[HIGH]** httpx version pinned to `>=0.24.0,<0.25.0` to fix crashes caused by unpinned dependency

### Fixed
- ChromaDB `persist()` compatibility — gracefully handles ChromaDB 0.4.0+ which auto-persists
- `register_test` decorator now properly returns the decorated class (was returning `None`)
- Getter/setter consistency for `embedding_provider` and `embedding_model` — setters now accept empty values matching getter defaults
- Empty base URL strings are now filtered out instead of being passed through to model constructors
- Fragile error-message string matching in RAG poisoning replaced with specific exception type handling (`ImportError`, `ConnectionError`, `ValueError`, etc.)
- Removed stale custom benchmark cache
- Release workflow no longer overwrites manually written release notes

### Changed
- Minimum Python version raised from 3.7 to 3.9 (required by langchain 0.3.x)
- LangChain imports updated for 0.3.x compatibility:
  - `langchain.schema` → `langchain_core.messages` / `langchain_core.documents`
  - `langchain.chat_models` → `langchain_community.chat_models`
  - Pydantic v1 field introspection → Pydantic v2 with v1 fallback
- Test organization: AppConfig, helper function, and TestStatus tests moved from `test_is_response_list.py` into dedicated test files
- Removed unused variable assignments in test code

## [2.0.0]

- Fuzzer 2.0 release
