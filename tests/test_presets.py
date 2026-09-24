"""Unit tests for the AKSAN Melankolik Asi preset."""

from composer160.core.parameters import T1_PARAMETER_IDS
from composer160.presets.aksan import aksan_preset


def test_aksan_preset_t1_complete():
    vec = aksan_preset()
    assert vec.t1_complete(), "AKSAN preset must have all 12 T1 parameters set"
    for pid in T1_PARAMETER_IDS:
        assert vec.is_set(pid), f"T1 parameter {pid} must be set"


def test_aksan_signature_sound():
    vec = aksan_preset()

    # Tonal & Tempo identity
    assert vec.get(1) == "A"
    assert vec.get(2) == "Minor"
    assert vec.get(3) == "Aeolian"
    assert vec.get(8) == 86
    assert vec.get(11) == "4/4"
    assert vec.get(15) == "Straight"

    # Emotion & Aesthetic (#050508 minimalist brutalism)
    assert vec.get(100) == "Melancholy"
    assert vec.get(72) == 2  # Dark timbre brightness
    assert vec.get(73) == 4  # Lush warm tape saturation
    assert vec.get(75) == "Hybrid"
    assert vec.get(79) == "mp"

    # Signature instruments
    stems = vec.get(144)
    assert "saz/bağlama" in stems
    assert "duduk" in stems
    assert "electric guitar" in stems
    assert "upright bass" in stems
    assert "soft drum brushes" in stems

    # Vocal & Bilingual Prosody
    assert vec.get(117) == "Lead"
    assert vec.get(119) == "Raspy"
    assert "TR80/EN20" in vec.get(121)
    assert vec.get(126) >= 4  # Speech-natural prosody to prevent unsingable output

    # Exclusions (anti-patterns)
    avoid = vec.get(135)
    assert "trap hats" in avoid
    assert "autotune" in avoid
    assert "key change" in avoid

    neg = vec.get(149)
    assert "trap hats" in neg
    assert "autotune ladder" in neg


def test_aksan_section_map_arithmetic():
    vec = aksan_preset()
    section_map = vec.get(130)
    total_bars = vec.get(134)

    assert isinstance(section_map, list)
    sum_bars = sum(bars for _, bars in section_map)
    assert sum_bars == total_bars == 75

    energies = vec.get(131)
    assert len(energies) == len(section_map)
