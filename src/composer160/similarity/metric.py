"""COMPOSER-160 v3.0 Vector Similarity Metric.

Calculates normalized multi-tiered distance d̃(A, B) ∈ [0, 1] between two
parameter vectors, blending continuous scalar precision with categorical
Hamming and ordered rank penalties.
"""

import math
from typing import Any

from composer160.core.parameters import PARAMETER_REGISTRY
from composer160.core.types import ParamType, Tier
from composer160.core.vector import ParameterVector

TIER_WEIGHTS: dict[Tier, float] = {
    Tier.T1: 4.0,
    Tier.T2: 2.0,
    Tier.T3: 1.0,
}


def distance(a: ParameterVector, b: ParameterVector, alpha: float = 0.5) -> float:
    """Compute the normalized distance d̃(A, B) ∈ [0, 1].

    Args:
        a: First ParameterVector.
        b: Second ParameterVector.
        alpha: Weight balancing scalar precision vs. categorical identity (default: 0.5).

    Returns:
        Float strictly bounded in [0.0, 1.0], where 0.0 indicates identity and
        < 0.15 indicates 'effectively the same piece'.
    """
    alpha = max(0.0, min(1.0, float(alpha)))

    scalar_weighted_sq_diff = 0.0
    scalar_weight_sum = 0.0

    cat_weighted_penalty = 0.0
    cat_weight_sum = 0.0

    for pid in range(1, 161):
        va = a.get(pid)
        vb = b.get(pid)

        # Skip parameters unset in both
        if va == "auto" and vb == "auto":
            continue

        defn = PARAMETER_REGISTRY.get(pid)
        if defn is None:
            continue

        w = TIER_WEIGHTS.get(defn.tier, 1.0)

        # 1. Scalar Parameters (ParamType.S): normalized Euclidean component
        if defn.param_type == ParamType.S:
            try:
                val_a = float(va) if va != "auto" else 3.0
                val_b = float(vb) if vb != "auto" else 3.0
                diff = abs(val_a - val_b)
                scalar_weighted_sq_diff += w * (diff**2)
                scalar_weight_sum += w
            except (ValueError, TypeError):
                continue

        # 2. Ordered Categorical (ParamType.O): rank-normalized penalty
        elif defn.param_type == ParamType.O:
            if va == vb:
                penalty = 0.0
            elif va == "auto" or vb == "auto":
                penalty = 1.0
            else:
                ranks = defn.values
                if ranks and va in ranks and vb in ranks:
                    ra = ranks.index(va)
                    rb = ranks.index(vb)
                    r_span = len(ranks) - 1
                    penalty = abs(ra - rb) / r_span if r_span > 0 else 0.0
                else:
                    penalty = 1.0
            cat_weighted_penalty += w * penalty
            cat_weight_sum += w

        # 3. Categorical (ParamType.C), Boolean (ParamType.B), Timeline, and Numeric
        else:
            if va == vb:
                penalty = 0.0
            elif va == "auto" or vb == "auto":
                penalty = 1.0
            elif isinstance(va, (list, tuple, set)) and isinstance(vb, (list, tuple, set)):
                # Jaccard distance for multi-select lists
                sa = set(va)
                sb = set(vb)
                union = sa | sb
                inter = sa & sb
                penalty = 1.0 - (len(inter) / len(union)) if union else 0.0
            else:
                penalty = 1.0 if va != vb else 0.0

            cat_weighted_penalty += w * penalty
            cat_weight_sum += w

    # Calculate scalar term normalized by (5 - 1)² = 16
    if scalar_weight_sum > 0:
        scalar_term = math.sqrt(scalar_weighted_sq_diff / (16.0 * scalar_weight_sum))
    else:
        scalar_term = 0.0

    # Calculate categorical term
    if cat_weight_sum > 0:
        cat_term = cat_weighted_penalty / cat_weight_sum
    else:
        cat_term = 0.0

    # Blend
    if scalar_weight_sum > 0 and cat_weight_sum > 0:
        total_dist = (alpha * scalar_term) + ((1.0 - alpha) * cat_term)
    elif scalar_weight_sum > 0:
        total_dist = scalar_term
    else:
        total_dist = cat_term

    return max(0.0, min(1.0, float(total_dist)))
