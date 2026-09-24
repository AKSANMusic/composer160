"""COMPOSER-160 Core Type System.

Defines the parameter types, priority tiers, and domain categories
as specified in the COMPOSER-160 architecture.
"""

from enum import Enum, IntEnum


class ParamType(str, Enum):
    """Parameter type tags governing representation and validation.

    S: Scalar (①→⑤ continuous; integers or one decimal)
    N: Numeric with unit (e.g. BPM, LUFS, seconds, syllables/bar)
    C: Categorical, unordered (pick one unless marked multi)
    O: Ordered categorical (rank distance is meaningful)
    B: Boolean flag (on/off)
    T: Timeline / list (ordered structure, e.g. section map)
    """

    S = "scalar"
    N = "numeric"
    C = "categorical"
    O = "ordered"
    B = "boolean"
    T = "timeline"


class Tier(IntEnum):
    """Priority tiers — the single hierarchy governing resolution and output.

    T1 > T2 > T3:
    - T1 (Priority 1): Non-negotiable, always filled (12 fields)
    - T2 (Priority 2): High-impact, fill for anything user-facing (52 fields)
    - T3 (Priority 3): Refinement only (96 fields)
    """

    T1 = 1
    T2 = 2
    T3 = 3


class Domain(str, Enum):
    """The 20 controlled parameter domains (A through T)."""

    A = "Tonal Foundation"
    B = "Tempo & Meter"
    C = "Rhythm & Groove"
    D = "Melody"
    E = "Harmony"
    F = "Bass"
    G = "Texture & Counterpoint"
    H = "Orchestration & Timbre"
    I = "Dynamics & Expression"
    J = "Form & Structure"
    K = "Emotion & Narrative"
    L = "Production & Spatial"
    M = "Vocal"
    N = "Lyrics & Prosody"
    O = "Structure Timeline"
    P = "Exclusions"
    Q = "Reference Anchors"
    R = "Mix & Arrangement"
    S = "AI Generator Directives"
    T = "Project & Release Context"
