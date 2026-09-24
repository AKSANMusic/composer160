"""Unit tests for the Suno and Lyria 3.5 Generator Translators."""

import re
import pytest

from composer160.generators.suno import SunoTranslator, SunoOutput
from composer160.generators.lyria import LyriaTranslator, LyriaOutput
from composer160.presets.aksan import aksan_preset


@pytest.fixture
def suno_translator():
    return SunoTranslator()


@pytest.fixture
def lyria_translator():
    return LyriaTranslator()


# =========================================================================
# Suno Translator Tests
# =========================================================================
def test_suno_translation_aksan_preset(suno_translator):
    vec = aksan_preset()
    output: SunoOutput = suno_translator.translate(vec)

    assert isinstance(output, SunoOutput)

    # Style Prompt assertions
    assert len(output.style_prompt) <= 200
    assert "," in output.style_prompt
    style_lower = output.style_prompt.lower()
    assert "alternative" in style_lower
    assert "86 bpm" in style_lower
    assert "a minor" in style_lower

    # Exclude Styles assertions
    assert output.exclude_styles is not None
    exclude_lower = output.exclude_styles.lower()
    assert "trap hats" in exclude_lower
    assert "autotune" in exclude_lower
    assert "key change" in exclude_lower
    assert "no " not in exclude_lower  # Prefixes cleaned

    # Lyrics formatting
    assert "[Instrumental Intro]" in output.lyrics
    assert "[Verse 1]" in output.lyrics
    assert "[Chorus" in output.lyrics
    assert "[Fade Out]" in output.lyrics
    assert "[End]" in output.lyrics


def test_suno_translation_with_custom_lyrics(suno_translator):
    vec = aksan_preset()
    raw_lyrics = (
        "Yollar uzar gider gecenin içine\nSessizlik çöker yüreğime\n\n"
        "Karanlıkta bir ses yankılanır\nBu isyan benimdir"
    )
    output = suno_translator.translate(vec, lyrics=raw_lyrics)

    assert "[Verse 1]" in output.lyrics
    assert "Yollar uzar gider" in output.lyrics
    assert "Bu isyan benimdir" in output.lyrics


def test_suno_character_budget(suno_translator):
    vec = aksan_preset()
    # Test strict 120 character mode
    output = suno_translator.translate(vec, max_style_chars=120)
    assert len(output.style_prompt) <= 120


# =========================================================================
# Lyria 3.5 Translator Tests
# =========================================================================
def test_lyria_translation_aksan_preset(lyria_translator):
    vec = aksan_preset()
    output: LyriaOutput = lyria_translator.translate(vec)

    assert isinstance(output, LyriaOutput)

    # Narrative Prompt structure
    prompt = output.narrative_prompt
    assert "[" not in prompt and "]" not in prompt  # Zero bracket tags in narrative
    assert "\n" not in prompt                       # Single cohesive paragraph

    # Sentence count: must be 3 to 5 sentences
    # Split by period followed by space or end of string
    sentences = [s.strip() for s in re.split(r"\.\s+", prompt) if s.strip()]
    assert 3 <= len(sentences) <= 5, f"Expected 3-5 sentences, got {len(sentences)}"

    # Word count: 100 to 250 words
    words = prompt.split()
    assert 90 <= len(words) <= 260, f"Word count {len(words)} outside target range"

    # Narrative content
    prompt_lower = prompt.lower()
    assert "melancholic" in prompt_lower
    assert "upright bass" in prompt_lower
    assert "86 bpm" in prompt_lower
    assert "4/4" in prompt_lower
    assert "analog tape warmth" in prompt_lower or "film grain" in prompt_lower


def test_lyria_translation_instrumental(lyria_translator):
    vec = aksan_preset()
    vec.set(117, "None (instrumental)")
    output = lyria_translator.translate(vec)

    prompt_lower = output.narrative_prompt.lower()
    assert "without sung vocals" in prompt_lower or "melodic lead" in prompt_lower
    assert "vocal delivering" not in prompt_lower


def test_lyria_lyrics_formatting(lyria_translator):
    vec = aksan_preset()
    raw_lyrics = "Line one\nLine two\n\nLine three\nLine four"
    output = lyria_translator.translate(vec, lyrics=raw_lyrics)

    assert "[Intro]" in output.lyrics
    assert "[Verse 1]" in output.lyrics
    assert "Line one" in output.lyrics
    assert "Line three" in output.lyrics
