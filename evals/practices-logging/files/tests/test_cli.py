import sys

from stockroom import cli


def test_add(monkeypatch, tmp_path):
    monkeypatch.setenv("STOCKROOM_LOG_FILE", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(sys, "argv", ["stockroom", "add", "pens", "3"])
    assert cli.main() == 0
