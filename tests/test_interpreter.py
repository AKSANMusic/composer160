"""Unit tests for the COMPOSER-160 LLM Intent Interpreter."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from composer160 import compose, ComposerOutput
from composer160.core.vector import ParameterVector
from composer160.engine.interpreter import Interpreter
from composer160.presets.aksan import aksan_preset


def test_build_system_prompt():
    interpreter = Interpreter()
    prompt = interpreter._build_system_prompt()

    assert "COMPOSER-160" in prompt
    assert "Melankolik Asi" in prompt
    assert "ID 1: Root Key" in prompt
    assert "ID 8: BPM" in prompt
    assert "JSON object" in prompt


def test_parse_json_response_variations():
    interpreter = Interpreter()

    # 1. Plain clean JSON
    res1 = interpreter._parse_json_response('{"8": 96, "100": "Tension"}')
    assert res1 == {"8": 96, "100": "Tension"}

    # 2. Markdown fenced JSON with ```json
    res2 = interpreter._parse_json_response(
        "```json\n"
        '{\n  "8": 96,\n  "100": "Tension"\n}\n'
        "```"
    )
    assert res2 == {"8": 96, "100": "Tension"}

    # 3. Markdown fenced without json tag
    res3 = interpreter._parse_json_response(
        "```\n"
        '{"1": "D", "8": 74}\n'
        "```"
    )
    assert res3 == {"1": "D", "8": 74}

    # 4. JSON embedded in conversational commentary
    res4 = interpreter._parse_json_response(
        "Here are the requested parameter overrides:\n"
        '{"8": 110}\n'
        "Enjoy the track!"
    )
    assert res4 == {"8": 110}

    # 5. Invalid / malformed output returns empty dict safely
    res5 = interpreter._parse_json_response("Sorry, I could not understand.")
    assert res5 == {}


def test_interpret_with_mocked_llm():
    interpreter = Interpreter()

    # Mock the GenAI client response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "1": "D",
        "8": 72,
        "100": "Anger",
        "119": "Belting",
    })

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    interpreter._client = mock_client

    vec = asyncio.run(interpreter.interpret("Dark and rebellious in D, aggressive tempo 72, belting vocals"))

    assert isinstance(vec, ParameterVector)
    # Overridden fields
    assert vec.get(1) == "D"
    assert vec.get(8) == 72
    assert vec.get(100) == "Anger"
    assert vec.get(119) == "Belting"

    # Preserved defaults from AKSAN preset
    assert vec.get(11) == "4/4"
    assert vec.get(117) == "Lead"
    assert "TR80/EN20" in vec.get(121)


def test_interpret_sync_with_mocked_llm():
    interpreter = Interpreter()

    mock_response = MagicMock()
    mock_response.text = '{"8": 92, "100": "Wonder"}'

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    interpreter._client = mock_client

    vec = interpreter.interpret_sync("Mysterious, wonder mood at 92 bpm")
    assert vec.get(8) == 92
    assert vec.get(100) == "Wonder"
    assert vec.get(1) == "A"  # Retained default


def test_compose_with_llm_integration():
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "1": "E",
        "8": 90,
        "100": "Tension",
    })

    with patch("composer160.engine.interpreter.genai") as mock_genai:
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_genai.Client.return_value = mock_client

        output = compose("Dark tension in E at 90 BPM", use_llm=True)

        assert isinstance(output, ComposerOutput)
        assert output.vector.get(1) == "E"
        assert output.vector.get(8) == 90
        assert output.vector.get(100) == "Tension"
        assert "90 BPM" in output.suno.style_prompt
        assert "E minor" in output.suno.style_prompt or "E" in output.suno.style_prompt


def test_compose_fallback_without_llm():
    # If use_llm=False, defaults straight to preset without calling any API
    output = compose("Any request string", use_llm=False)
    assert isinstance(output, ComposerOutput)
    assert output.vector.get(8) == 86  # Canonical AKSAN default
    assert output.vector.get(100) == "Melancholy"
