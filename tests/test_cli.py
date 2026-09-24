"""Unit tests for the COMPOSER-160 CLI."""

import json
from pathlib import Path
import pytest

from composer160.cli import main


def test_cli_default_markdown(capsys):
    ret = main(["--no-llm"])
    assert ret == 0

    captured = capsys.readouterr()
    assert "### 1. SUNO ENGINE OUTPUT" in captured.out
    assert "### 2. LYRIA 3.5 ENGINE OUTPUT" in captured.out
    assert "### 3. COMPACT PARAMETER VECTOR" in captured.out


def test_cli_json_output(capsys):
    ret = main(["--no-llm", "-f", "json"])
    assert ret == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "suno" in data
    assert "lyria" in data
    assert "compact_vector" in data
    assert "section_map" in data


def test_cli_with_positional_prompt(capsys):
    ret = main(["Dark Anatolian alternative", "--no-llm"])
    assert ret == 0

    captured = capsys.readouterr()
    assert "dark alternative" in captured.out.lower() or "anatolian" in captured.out.lower()


def test_cli_with_flag_prompt(capsys):
    ret = main(["-p", "Cinematic score", "--no-llm", "-f", "json"])
    assert ret == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["suno"]["style_prompt"] is not None


def test_cli_with_lyrics_file(tmp_path, capsys):
    lyrics_file = tmp_path / "song_lyrics.txt"
    lyrics_file.write_text("Bir rüya gördüm dün gece\nHer yer karanlıktı", encoding="utf-8")

    ret = main(["--no-llm", "--lyrics", str(lyrics_file)])
    assert ret == 0

    captured = capsys.readouterr()
    assert "Bir rüya gördüm dün gece" in captured.out


def test_cli_load_c160_file(tmp_path, capsys):
    from composer160.presets.aksan import aksan_preset

    vec = aksan_preset()
    vec.set(8, 142)  # Set custom BPM
    filepath = tmp_path / "custom.c160"
    vec.save_to_file(filepath)

    ret = main(["--load", str(filepath), "--no-llm", "-f", "json"])
    assert ret == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["compact_vector"] is not None


def test_cli_interactive_flag(monkeypatch):
    from unittest.mock import MagicMock

    mock_repl = MagicMock()
    monkeypatch.setattr("composer160.repl.run_repl", mock_repl)

    ret = main(["--interactive", "--no-llm"])
    assert ret == 0
    assert mock_repl.called
    assert mock_repl.call_args.kwargs["use_llm"] is False
