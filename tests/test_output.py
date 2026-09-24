"""Unit tests for Output Formatter, Section Map, and Public compose() API."""

import json
from composer160 import compose, ComposerOutput
from composer160.output.section_map import Section, SectionMapBuilder
from composer160.output.notation import render_vector
from composer160.presets.aksan import aksan_preset


def test_section_map_builder():
    vec = aksan_preset()
    builder = SectionMapBuilder()
    sections = builder.build_from_vector(vec)

    assert len(sections) == 9
    assert all(isinstance(s, Section) for s in sections)
    assert sum(s.bars for s in sections) == 75

    map_str = builder.format_map(sections)
    assert "Intro4" in map_str
    assert "V12" in map_str
    assert "Ch12" in map_str
    assert " · " in map_str

    energy_str = builder.format_energy(sections)
    assert "②" in energy_str
    assert "⑤" in energy_str
    assert "·" in energy_str


def test_render_vector_notation():
    vec = aksan_preset()
    compact = render_vector(vec)

    assert "[KEY:Am]" in compact
    assert "[TONALITY:Minor/Aeolian]" in compact
    assert "[BPM:86]" in compact
    assert "[TIMESIG:4/4]" in compact
    assert "[EMOTION:Melancholy]" in compact
    assert "[MAP:" in compact
    assert "[ENERGY:" in compact
    assert "[ANCHORS:" in compact
    assert "[NEG:" in compact

    # Verify delegation on vector instance
    assert vec.to_compact() == compact


def test_composer_output_formatting():
    vec = aksan_preset()
    output = compose(vec)

    assert isinstance(output, ComposerOutput)
    assert output.vector is vec
    assert len(output.compact) > 0
    assert len(output.suno.style_prompt) > 0
    assert len(output.lyria.narrative_prompt) > 0

    # Test serialization to dict and JSON
    d = output.to_dict()
    assert "suno" in d
    assert "lyria" in d
    assert "compact_vector" in d
    assert "section_map" in d

    json_str = output.to_json()
    parsed = json.loads(json_str)
    assert parsed["suno"]["style_prompt"] == output.suno.style_prompt

    # Test markdown formatting
    md = output.to_markdown()
    assert "### 1. SUNO ENGINE OUTPUT" in md
    assert "### 2. LYRIA 3.5 ENGINE OUTPUT" in md
    assert "### 3. COMPACT PARAMETER VECTOR & SECTION MAP" in md


def test_public_compose_api():
    # Calling with a string request
    out1 = compose("Dark rebellious ballad with duduk")
    assert isinstance(out1, ComposerOutput)
    assert out1.suno.style_prompt is not None
    assert all(c.passed for c in out1.checks)

    # Calling with custom lyrics
    custom_lyrics = "Gözlerin bir yangın yeri\nBeni kül eyle\n\nBu gece isyanım var"
    out2 = compose(lyrics=custom_lyrics)
    assert "Gözlerin bir yangın yeri" in out2.suno.lyrics
    assert "Gözlerin bir yangın yeri" in out2.lyria.lyrics
