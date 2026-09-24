"""Unit tests for ParameterVector persistence (.c160 JSON format) and REPL operations."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

from composer160.core.vector import ParameterVector
from composer160.presets.aksan import aksan_preset
from composer160.repl import (
    REPLSession,
    compute_vector_diff,
    format_vector_diff,
)


def test_save_and_load_aksan_roundtrip(tmp_path: Path):
    """Verify that saving and loading an AKSAN preset vector retains 100% fidelity."""
    original = aksan_preset()
    filepath = tmp_path / "aksan_test.c160"

    # Save to disk
    original.save_to_file(filepath)
    assert filepath.is_file()

    # Load from disk
    loaded = ParameterVector.load_from_file(filepath)

    # 1. Values match
    assert loaded._values == original._values

    # 2. Assumed and locked match
    assert loaded._assumed == original._assumed
    assert loaded._locked == original._locked

    # 3. Section map tuples in #130 are preserved
    assert loaded.get(130) == original.get(130)
    for section in loaded.get(130):
        assert isinstance(section, tuple)
        assert len(section) == 2
        assert isinstance(section[0], str)
        assert isinstance(section[1], int)

    # 4. T1 completeness is preserved
    assert loaded.t1_complete() is True
    assert len(loaded) == len(original)


def test_save_creates_parent_directories(tmp_path: Path):
    """Verify save_to_file creates nested parent directories automatically."""
    vec = ParameterVector()
    vec.set(1, "E")
    vec.set(8, 120)

    deep_path = tmp_path / "deeply" / "nested" / "folder" / "track.c160"
    vec.save_to_file(deep_path)

    assert deep_path.is_file()
    loaded = ParameterVector.load_from_file(deep_path)
    assert loaded.get(1) == "E"
    assert loaded.get(8) == 120


def test_load_nonexistent_file_raises_filenotfound(tmp_path: Path):
    """Attempting to load a nonexistent file raises FileNotFoundError."""
    missing_path = tmp_path / "does_not_exist.c160"
    with pytest.raises(FileNotFoundError, match="File not found"):
        ParameterVector.load_from_file(missing_path)


def test_load_malformed_json_raises_valueerror(tmp_path: Path):
    """Loading a corrupt or non-JSON file raises ValueError."""
    corrupt_file = tmp_path / "corrupt.c160"
    corrupt_file.write_text("{ incomplete json...", encoding="utf-8")

    with pytest.raises(ValueError, match="Malformed .c160 JSON file"):
        ParameterVector.load_from_file(corrupt_file)


def test_load_unsupported_format_raises_valueerror(tmp_path: Path):
    """Loading a JSON file without 'format': 'c160' raises ValueError."""
    invalid_file = tmp_path / "wrong_format.json"
    invalid_file.write_text(
        json.dumps({"format": "other_format", "values": {}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported format"):
        ParameterVector.load_from_file(invalid_file)


def test_save_and_load_with_assumed_parameters(tmp_path: Path):
    """Verify that assumed vs locked flags are correctly persisted and restored."""
    vec = ParameterVector()
    vec.set(1, "C", assumed=False)
    vec.set(2, "Major", assumed=True)
    vec.set(8, 100, assumed=True)

    filepath = tmp_path / "assumed.c160"
    vec.save_to_file(filepath)

    loaded = ParameterVector.load_from_file(filepath)
    assert loaded.get(1) == "C"
    assert loaded.get(2) == "Major"
    assert loaded.get(8) == 100

    # Check assumed status
    assumed_fields = {pid: name for pid, name, _ in loaded.assumed_t1_fields()}
    assert 2 in assumed_fields
    assert 8 in assumed_fields
    assert 1 not in assumed_fields


def test_repl_diff_calculation_and_formatting():
    """Verify vector diff computation and human-readable formatting."""
    vec_a = aksan_preset()
    vec_b = vec_a.copy()

    # Modify two parameters
    vec_b.set(8, 108)  # BPM changed from 86 to 108
    vec_b.set(1, "E")  # Root Key changed from A to E

    diffs = compute_vector_diff(vec_a, vec_b)
    assert len(diffs) == 2
    assert diffs[8] == (86, 108)
    assert diffs[1] == ("A", "E")

    formatted = format_vector_diff(diffs)
    assert "Changes applied (2 parameters modified):" in formatted
    assert "#  1 Root Key [T1]: 'A' ➔ 'E'" in formatted
    assert "#  8 BPM [T1]: 86 ➔ 108" in formatted

    # Test empty diff
    empty_diff = compute_vector_diff(vec_a, vec_a)
    assert len(empty_diff) == 0
    assert "No parameter changes detected" in format_vector_diff(empty_diff)


def test_repl_session_save_and_load_workflow(tmp_path: Path):
    """Verify the full save, modify, reset, and load lifecycle inside a REPLSession."""
    save_file = tmp_path / "my_track.c160"

    session = REPLSession(use_llm=False)
    # Modify active vector
    session.active_vector.set(8, 128)
    session.active_vector.set(1, "F#")

    # Save via REPL command
    session._handle_save(str(save_file))
    assert save_file.is_file()

    # Reset session back to original
    session._handle_reset()
    assert session.active_vector.get(8) == 86
    assert session.active_vector.get(1) == "A"

    # Reload via REPL command
    session._handle_load(str(save_file))
    assert session.active_vector.get(8) == 128
    assert session.active_vector.get(1) == "F#"


def test_repl_commands_execution(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verify that all REPL slash commands execute cleanly without error."""
    session = REPLSession(use_llm=False)

    # 1. /show
    assert session.handle_command("/show") is True
    out = capsys.readouterr().out
    assert "SUNO STYLE PROMPT" in out
    assert "GOOGLE LYRIA 3.5 NARRATIVE" in out

    # 2. /diff (initially empty)
    assert session.handle_command("/diff") is True
    out = capsys.readouterr().out
    assert "No parameter changes detected" in out

    # 3. /compact
    assert session.handle_command("/compact") is True
    out = capsys.readouterr().out
    assert "Compact Bracket Notation" in out

    # 4. /validate
    assert session.handle_command("/validate") is True
    out = capsys.readouterr().out
    assert "C1–C7 Validation Results" in out
    assert "PASS" in out

    # 5. /lyrics
    assert session.handle_command("/lyrics Bir akşam vakti...") is True
    assert session.lyrics == "Bir akşam vakti..."

    # 6. /help
    assert session.handle_command("/help") is True
    out = capsys.readouterr().out
    assert "COMPOSER-160 REPL Commands" in out

    # 7. /exit, /quit, /q
    assert session.handle_command("/exit") is False
    assert session.handle_command("/quit") is False
    assert session.handle_command("/q") is False


def test_repl_apply_tweak_with_mocked_llm():
    """Verify natural language prompt tweak updates vector and records history."""
    session = REPLSession(use_llm=True)

    # Mock the LLM client
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "8": 94,
        "100": "Anger",
        "119": "Belting",
    })
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    session.interpreter._client = mock_client

    # Apply natural language tweak
    diffs = session.apply_tweak("Make the tempo 94 with angry belting vocals")

    assert len(diffs) == 3
    assert diffs[8] == (86, 94)
    assert diffs[100] == ("Melancholy", "Anger")
    assert diffs[119] == ("Raspy", "Belting")

    # Active vector reflects updates
    assert session.active_vector.get(8) == 94
    assert session.active_vector.get(100) == "Anger"
    assert session.active_vector.get(119) == "Belting"

    # History logged
    assert len(session.history) == 1
    prompt, recorded_diffs = session.history[0]
    assert prompt == "Make the tempo 94 with angry belting vocals"
    assert recorded_diffs == diffs
