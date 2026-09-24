"""Multi-Objective Evaluation Functions for COMPOSER-160.

Evaluates candidates along 4 competing fitness dimensions:
1. f_intent: Alignment with the user's specific request.
2. f_identity: Loyalty to the core AKSAN 'Melankolik Asi' soundscape.
3. f_novelty: Perceptual surprise, modal complexity, and cliché avoidance.
4. f_validity: Mathematical and musical coherence (C1–C7 constraint satisfaction).
"""

from __future__ import annotations

import re
from typing import Any

from composer160.core.vector import ParameterVector
from composer160.presets.aksan import aksan_preset
from composer160.similarity.metric import distance
from composer160.validation.checks import Validator


def f_intent(vec: ParameterVector, target_vec: ParameterVector | str) -> float:
    """Evaluate how closely a vector satisfies the user's target intent.

    Args:
        vec: The candidate ParameterVector to evaluate.
        target_vec: The user's target ParameterVector (e.g. from initial fast LLM interpretation)
            or a prompt string to score against keywords.

    Returns:
        Score between 0.0 (distant) and 1.0 (exact match).
    """
    if isinstance(target_vec, ParameterVector):
        dist = distance(vec, target_vec)
        return max(0.0, min(1.0, 1.0 - dist))

    # Keyword-based fallback scoring if raw prompt string is passed
    prompt_lower = target_vec.lower()
    score_points = 0
    total_checks = 0

    # 1. Check tempo intent
    bpm_match = re.search(r"\b(\d{2,3})\s*(?:bpm)?\b", prompt_lower)
    if bpm_match:
        target_bpm = int(bpm_match.group(1))
        cand_bpm = vec.get(8)
        if isinstance(cand_bpm, (int, float)):
            total_checks += 1
            bpm_diff = abs(cand_bpm - target_bpm)
            score_points += max(0.0, 1.0 - (bpm_diff / 50.0))

    # 2. Check mood intent
    for mood in ("melancholy", "anger", "grief", "rebellion", "tension", "longing", "calm"):
        if mood in prompt_lower:
            total_checks += 1
            cand_mood = str(vec.get(100)).lower()
            if mood in cand_mood:
                score_points += 1.0
            elif vec.get(101) != "auto":
                score_points += 0.5

    # 3. Check instrument mentions
    for inst in ("duduk", "guitar", "bass", "saz", "bağlama", "drums", "vocal"):
        if inst in prompt_lower:
            total_checks += 1
            stems = [str(s).lower() for s in (vec.get(144) or []) if s != "auto"]
            fams = [str(f).lower() for f in (vec.get(68) or []) if f != "auto"]
            if any(inst in s for s in stems) or any(inst in f for f in fams):
                score_points += 1.0

    if total_checks == 0:
        return 0.8  # Neutral intent score if prompt had no extractable constraints

    return max(0.0, min(1.0, score_points / total_checks))


def f_identity(
    vec: ParameterVector,
    base_preset: ParameterVector | None = None,
) -> float:
    """Evaluate aesthetic loyalty to the core AKSAN 'Melankolik Asi' soundscape.

    Returns:
        Score between 0.0 (loss of identity) and 1.0 (pure AKSAN canon).
    """
    base = base_preset or aksan_preset()
    dist = distance(vec, base)
    base_score = 1.0 - dist

    # Extra weight on signature identity anchors:
    # Duduk / Saz / Upright Bass / Tape saturation presence
    bonus = 0.0
    stems = [str(s).lower() for s in (vec.get(144) or []) if s != "auto"]
    if any("saz" in s or "bağlama" in s for s in stems):
        bonus += 0.04
    if any("duduk" in s for s in stems):
        bonus += 0.04
    if any("upright bass" in s or "acoustic bass" in s for s in stems):
        bonus += 0.04

    # Dark timbre check (#72 <= 2)
    brightness = vec.get(72)
    if isinstance(brightness, (int, float)) and brightness <= 2:
        bonus += 0.03

    return max(0.0, min(1.0, base_score + bonus))


def f_novelty(vec: ParameterVector) -> float:
    """Evaluate aesthetic novelty, modal depth, and non-cliché surprises.

    Rewards:
    - Modal or unexpected scale choices (Phrygian, Dorian, Melodic minor)
    - Asymmetric or syncopated meter (7/8, 5/8, syncopation level >= 3)
    - Harmonic extension (7ths, 9ths, suspended chords, subtle dissonance)
    - Creative dynamic shapes and spatial depth (plate, cathedral, wide width)
    """
    score = 0.0

    # 1. Harmonic & Modal richness (up to 0.3)
    mode = str(vec.get(3)).lower()
    if mode in ("phrygian", "dorian", "harmonic minor", "melodic minor"):
        score += 0.15
    elif mode == "aeolian":
        score += 0.08

    chords = str(vec.get(40)).lower()
    if any(k in chords for k in ("7th", "9th", "sus", "extended", "altered")):
        score += 0.10
    dissonance = vec.get(50)
    if isinstance(dissonance, (int, float)) and dissonance >= 2:
        score += 0.05

    # 2. Rhythmic exploration (up to 0.25)
    time_sig = str(vec.get(11))
    if time_sig in ("7/8", "5/8", "6/8", "9/8"):
        score += 0.15
    elif time_sig == "4/4":
        score += 0.05

    syncopation = vec.get(19)
    if isinstance(syncopation, (int, float)) and syncopation >= 3:
        score += 0.10

    # 3. Dynamic and Articulation boldness (up to 0.25)
    dyn_range = str(vec.get(80)).lower()
    if "wide" in dyn_range or "extreme" in dyn_range:
        score += 0.10
    cliche_avoid = vec.get(137)
    if isinstance(cliche_avoid, (int, float)) and cliche_avoid >= 4:
        score += 0.10
    ornamentation = str(vec.get(36)).lower()
    if "microtonal" in ornamentation or "elaborate" in ornamentation:
        score += 0.05

    # 4. Spatial & Master textures (up to 0.2)
    spatial = str(vec.get(108)).lower()
    if spatial in ("cinematic", "infinite", "cathedral"):
        score += 0.10
    sat = str(vec.get(113)).lower()
    if "film grain" in sat or "tape" in sat:
        score += 0.10

    return max(0.0, min(1.0, score))


def f_validity(vec: ParameterVector, validator: Validator | None = None) -> float:
    """Evaluate structural, harmonic, and mathematical validity (C1–C7 checks).

    Returns:
        Score between 0.0 (fatal structural failure) and 1.0 (flawless pass).
    """
    v = validator or Validator()
    checks = v.validate(vec)

    if not checks:
        return 1.0

    total_weight = 0.0
    earned_weight = 0.0

    for c in checks:
        # C1 (T1 completeness) and C3 (duration math) have higher priority
        weight = 2.0 if c.check_id in ("C1", "C3") else 1.0
        total_weight += weight

        if c.passed:
            earned_weight += weight
        elif c.auto_fixed:
            earned_weight += weight * 0.85
        else:
            earned_weight += 0.0

    score = earned_weight / total_weight if total_weight > 0 else 1.0

    # Heavy penalty if T1 parameters are incomplete
    if not vec.t1_complete():
        score *= 0.5

    return max(0.0, min(1.0, score))


def evaluate_objectives(
    vec: ParameterVector,
    target_vec: ParameterVector,
    base_preset: ParameterVector | None = None,
    validator: Validator | None = None,
) -> tuple[float, float, float, float]:
    """Calculate all 4 objective scores for a candidate vector.

    Returns:
        Tuple of (f_intent, f_identity, f_novelty, f_validity)
    """
    return (
        f_intent(vec, target_vec),
        f_identity(vec, base_preset),
        f_novelty(vec),
        f_validity(vec, validator),
    )
