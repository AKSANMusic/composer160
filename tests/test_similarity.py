"""Unit tests for the COMPOSER-160 v3.0 Vector Similarity Metric."""

import pytest
from composer160.core.vector import ParameterVector
from composer160.presets.aksan import aksan_preset
from composer160.similarity.metric import distance


def test_identical_vectors_have_zero_distance():
    vec_a = aksan_preset()
    vec_b = aksan_preset()
    d = distance(vec_a, vec_b)
    assert d == 0.0, f"Expected 0.0 distance for identical vectors, got {d}"


def test_distance_is_strictly_bounded_between_0_and_1():
    vec_a = aksan_preset()
    vec_b = ParameterVector()
    # Create an opposing vector with inverted traits
    vec_b.set(1, "C")
    vec_b.set(2, "Major")
    vec_b.set(8, 140)
    vec_b.set(11, "3/4")
    vec_b.set(15, "Swing")
    vec_b.set(26, "None (textural)")
    vec_b.set(45, "Pop loop")
    vec_b.set(68, ["Synth", "Percussion"])
    vec_b.set(75, "Electronic")
    vec_b.set(100, "Joy")
    vec_b.set(107, ["Hip-hop"])
    vec_b.set(117, "None (instrumental)")
    vec_b.set(72, 5)  # Max brightness
    vec_b.set(73, 1)  # Min warmth

    d = distance(vec_a, vec_b)
    assert 0.0 <= d <= 1.0
    assert d > 0.3, f"Expected noticeable distance between opposing vectors, got {d}"


def test_tier_weighting_t1_greater_than_t3():
    base = aksan_preset()

    # Vector 1: change a T1 parameter (#1 Root Key, weight 4.0)
    vec_t1 = base.copy()
    vec_t1.set(1, "F♯")
    d_t1 = distance(base, vec_t1, alpha=0.0)  # Categorical distance only

    # Vector 2: change a T3 parameter (#36 Ornamentation, weight 1.0)
    vec_t3 = base.copy()
    vec_t3.set(36, "Rich")
    d_t3 = distance(base, vec_t3, alpha=0.0)

    assert d_t1 > d_t3, f"T1 distance ({d_t1}) must exceed T3 distance ({d_t3})"


def test_ordered_categorical_rank_penalty():
    base = aksan_preset()
    # #79 Base Dynamic values: ("pp", "p", "mp", "mf", "f", "ff")
    base.set(79, "pp")

    near_vec = base.copy()
    near_vec.set(79, "p")   # 1 rank away

    far_vec = base.copy()
    far_vec.set(79, "ff")   # 5 ranks away (max span)

    d_near = distance(base, near_vec, alpha=0.0)
    d_far = distance(base, far_vec, alpha=0.0)

    assert d_near < d_far, f"Near rank distance ({d_near}) must be less than far rank distance ({d_far})"


def test_alpha_weighting_scalar_vs_categorical():
    base = aksan_preset()

    # Change only a scalar parameter (#72 Timbre Brightness)
    vec_scalar = base.copy()
    vec_scalar.set(72, 5)  # was 2, delta = 3

    # Purely scalar evaluation (alpha=1.0)
    d_scalar = distance(base, vec_scalar, alpha=1.0)
    assert d_scalar > 0.0

    # Purely categorical evaluation (alpha=0.0) ignores scalar differences
    d_cat = distance(base, vec_scalar, alpha=0.0)
    assert d_cat == 0.0
