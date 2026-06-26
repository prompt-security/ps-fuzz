import builtins
import sys

import pytest

from ps_fuzz import cli
from ps_fuzz.logo import _print_unicode_safe


def test_cli_list_attacks_smoke_without_api(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prompt-security-fuzzer", "--list-attacks"])
    monkeypatch.setattr(cli, "print_logo", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "Available attacks:" in output
    assert "amnesia" in output
    assert "rag_poisoning" in output


def test_cli_list_providers_smoke_without_api(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prompt-security-fuzzer", "--list-providers"])
    monkeypatch.setattr(cli, "print_logo", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "Available providers:" in output
    assert "open_ai" in output
    assert "ollama" in output


def test_print_unicode_safe_falls_back_after_unicode_encode_error(monkeypatch):
    class Cp1251Stdout:
        encoding = "cp1251"

    calls = []

    def fake_print(value):
        calls.append(value)
        if len(calls) == 1:
            raise UnicodeEncodeError("cp1251", "░", 0, 1, "character maps to <undefined>")

    monkeypatch.setattr(sys, "stdout", Cp1251Stdout())
    monkeypatch.setattr(builtins, "print", fake_print)

    _print_unicode_safe("░")

    assert calls == ["░", "?"]
