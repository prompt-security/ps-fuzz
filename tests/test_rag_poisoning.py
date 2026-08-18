from unittest.mock import MagicMock

from ps_fuzz.attacks.rag_poisoning import TestRAGPoisoning


def test_rag_poisoning_uses_the_modern_retriever_invoke_api():
    """LangChain 1.x retrievers are Runnables and use invoke()."""
    attack = TestRAGPoisoning(MagicMock(), MagicMock())
    retriever = MagicMock()
    retriever.invoke.return_value = [MagicMock()]
    attack.vectorstore = MagicMock()
    attack.vectorstore.as_retriever.return_value = retriever

    assert attack._retrieve_relevant_documents("test query") == retriever.invoke.return_value
    retriever.invoke.assert_called_once_with("test query")
