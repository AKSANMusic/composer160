"""Unit tests for the COMPOSER-160 C1–C7 Validation Engine."""

import pytest
from composer160.core.vector import ParameterVector
from composer160.presets.aksan import aksan_preset
from composer160.validation.checks import Validator


@pytest.fixture
def validator():
    return Validator()


def test_aksan_preset_passes_all_checks(validator):
    vec = aksan_preset()
    results = validator.validate(vec)
    assert len(results) == 7
    for r in results:
        assert r.passed, f"Check {r.check_id} failed on aksan_preset: {r.message}"


# =========================================================================
# C1: Tier Completeness
# =========================================================================
def test_c1_tier_completeness_failure(validator):
    vec = ParameterVector()
    vec.set(1, "A")
    # All other 11 T1 fields missing
    res = validator._c1_tier_completeness(vec)
    assert not res.passed
    assert res.check_id == "C1"
    assert "Missing 11" in res.message


# =========================================================================
# C2: Tonality Topology
# =========================================================================
def test_c2_atonal_with_mode_fails(validator):
    vec = aksan_preset()
    vec.set(2, "Atonal")
    vec.set(3, "Dorian")
    res = validator._c2_tonality_topology(vec)
    assert not res.passed
    assert "forbids #3 Mode" in res.message


def test_c2_atonal_with_functional_progression_fails(validator):
    vec = aksan_preset()
    vec.set(2, "Atonal")
    vec.set(3, "auto")
    vec.set(45, "Functional")
    res = validator._c2_tonality_topology(vec)
    assert not res.passed
    assert "forbids Functional progression" in res.message


def test_c2_modal_without_mode_fails(validator):
    vec = aksan_preset()
    vec.set(2, "Modal")
    vec.set(3, "auto")
    res = validator._c2_tonality_topology(vec)
    assert not res.passed
    assert "Modal tonality requires #3 Mode" in res.message


# =========================================================================
# C3: Length Chain
# =========================================================================
def test_c3_length_chain_deviation_fails(validator):
    vec = aksan_preset()
    # 75 bars @ 86 BPM ≈ 209.3s. Setting target duration to 100s should fail (>5% deviation)
    vec.set(158, 100)
    res = validator._c3_length_chain(vec)
    assert not res.passed
    assert "deviates from #158 Target Duration" in res.message


def test_c3_length_chain_duration_category_mismatch(validator):
    vec = aksan_preset()
    # 75 bars @ 86 BPM ≈ 209.3s (Medium 3-5 min). Setting category to "Short (<2)" should fail
    vec.set(158, "auto")
    vec.set(88, "Short (<2)")
    res = validator._c3_length_chain(vec)
    assert not res.passed
    assert "inconsistent with #88 Duration category" in res.message


# =========================================================================
# C4: Energy Coherence
# =========================================================================
def test_c4_rising_curve_with_early_peak_fails(validator):
    vec = aksan_preset()
    vec.set(102, "Rising")
    # Energy peaks immediately at the intro
    vec.set(131, [5, 4, 3, 2, 1])
    res = validator._c4_energy_coherence(vec)
    assert not res.passed
    assert "Rising energy curve conflicts with peak energy in the opening" in res.message


def test_c4_falling_curve_with_late_peak_fails(validator):
    vec = aksan_preset()
    vec.set(102, "Falling")
    # Energy peaks at the very end
    vec.set(131, [1, 2, 3, 4, 5])
    res = validator._c4_energy_coherence(vec)
    assert not res.passed
    assert "Falling energy curve conflicts with peak energy at the track conclusion" in res.message


def test_c4_tension_climax_extremes_fail(validator):
    vec = aksan_preset()
    vec.set(103, 1)  # Low tension
    vec.set(95, 5)   # Epic climax
    res = validator._c4_energy_coherence(vec)
    assert not res.passed
    assert "contradicts Climax Intensity=5 (epic)" in res.message


# =========================================================================
# C5: Vocal Chain
# =========================================================================
def test_c5_vocal_missing_language_fails(validator):
    vec = aksan_preset()
    vec.set(117, "Lead")
    vec.set(121, "auto")
    res = validator._c5_vocal_chain(vec)
    assert not res.passed
    assert "requires #121 Language(s) to be set" in res.message


def test_c5_vocal_missing_style_fails(validator):
    vec = aksan_preset()
    vec.set(117, "Lead")
    vec.set(119, "auto")
    res = validator._c5_vocal_chain(vec)
    assert not res.passed
    assert "requires #119 Vocal Style to be set" in res.message


def test_c5_non_english_low_prosody_fails(validator):
    vec = aksan_preset()
    vec.set(117, "Lead")
    vec.set(121, ["TR80/EN20"])
    vec.set(126, 2)  # Prosody fit < 3
    res = validator._c5_vocal_chain(vec)
    assert not res.passed
    assert "requires Prosody Fit #126 >= 3" in res.message


def test_c5_instrumental_passes_without_vocal_params(validator):
    vec = aksan_preset()
    vec.set(117, "None (instrumental)")
    vec.set(121, "auto")
    vec.set(119, "auto")
    res = validator._c5_vocal_chain(vec)
    assert res.passed
    assert "Instrumental" in res.message


# =========================================================================
# C6: Map Arithmetic
# =========================================================================
def test_c6_map_arithmetic_mismatch_fails(validator):
    vec = aksan_preset()
    # Sections sum to 75 bars, but Total Bars says 90
    vec.set(134, 90)
    res = validator._c6_map_arithmetic(vec)
    assert not res.passed
    assert "sums to 75 bars, but #134 Total Bars specifies 90 bars" in res.message


def test_c6_map_arithmetic_string_format_passes(validator):
    vec = aksan_preset()
    vec.set(130, "Intro8 · V16 · Pre8 · Ch16 · Outro8")
    vec.set(134, 56)
    res = validator._c6_map_arithmetic(vec)
    assert res.passed


# =========================================================================
# C7: Exclusion Coverage
# =========================================================================
def test_c7_uncovered_exclusion_fails(validator):
    vec = aksan_preset()
    # Add a new forbidden element to #135 that is not in #149
    vec.set(135, ["trap hats", "accordion_solo_riff"])
    res = validator._c7_exclusion_coverage(vec)
    assert not res.passed
    assert "accordion_solo_riff" in res.message


def test_c7_forbidden_instrument_leak_fails(validator):
    vec = aksan_preset()
    vec.set(136, ["keytar"])
    vec.set(68, ["Strings", "keytar"])  # Leaked into positive instruments
    res = validator._c7_exclusion_coverage(vec)
    assert not res.passed
    assert "Forbidden instrument(s) leaked into positive arrangement" in res.message
