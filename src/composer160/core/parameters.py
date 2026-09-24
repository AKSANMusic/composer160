"""COMPOSER-160 Parameter Catalog and Registry.

The single source of truth for the controlled vocabulary of 160 parameters
across 20 domains (A through T), typed and categorized by priority tiers.
Exactly 12 T1, 52 T2, and 96 T3 parameters.
"""

from dataclasses import dataclass
from typing import Any, Sequence

from composer160.core.types import Domain, ParamType, Tier


@dataclass(frozen=True)
class ParameterDef:
    """Immutable definition of a single COMPOSER-160 parameter."""

    id: int
    name: str
    param_type: ParamType
    tier: Tier
    domain: Domain
    values: list[str] | tuple[str, ...] | None = None
    multi: bool = False
    unit: str | None = None
    default: Any = "auto"


# The 12 canonical T1 parameter IDs that shape ~80% of perceptual impact
T1_PARAMETER_IDS: tuple[int, ...] = (
    1,    # Root Key
    2,    # Tonality
    8,    # BPM
    11,   # Time Signature
    15,   # Groove Feel
    26,   # Melodic Presence
    45,   # Progression Type
    68,   # Primary Instrument Family
    75,   # Acoustic↔Electronic
    100,  # Primary Emotion
    107,  # Genre Reference
    117,  # Vocal Presence
)


PARAMETER_REGISTRY: dict[int, ParameterDef] = {
    # =========================================================================
    # Domain A: Tonal Foundation [1–7]
    # =========================================================================
    1: ParameterDef(
        id=1, name="Root Key", param_type=ParamType.C, tier=Tier.T1, domain=Domain.A,
        values=("C", "C♯", "D", "E♭", "E", "F", "F♯", "G", "A♭", "A", "B♭", "B"),
    ),
    2: ParameterDef(
        id=2, name="Tonality", param_type=ParamType.C, tier=Tier.T1, domain=Domain.A,
        values=("Major", "Minor", "Modal", "Atonal", "Polytonal"),
    ),
    3: ParameterDef(
        id=3, name="Mode", param_type=ParamType.C, tier=Tier.T2, domain=Domain.A,
        values=("Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"),
    ),
    4: ParameterDef(
        id=4, name="Scale Type", param_type=ParamType.C, tier=Tier.T2, domain=Domain.A,
        values=("Diatonic", "Pentatonic", "Blues", "Whole-tone", "Chromatic", "Octatonic", "Harmonic/melodic minor"),
    ),
    5: ParameterDef(
        id=5, name="Tonal Stability", param_type=ParamType.S, tier=Tier.T3, domain=Domain.A,
        values=("1", "2", "3", "4", "5"),
    ),
    6: ParameterDef(
        id=6, name="Modulation Frequency", param_type=ParamType.O, tier=Tier.T3, domain=Domain.A,
        values=("None", "Rare", "Occasional", "Frequent"),
    ),
    7: ParameterDef(
        id=7, name="Modulation Distance", param_type=ParamType.O, tier=Tier.T3, domain=Domain.A,
        values=("None", "Close keys", "Relative", "Distant", "Enharmonic"),
    ),

    # =========================================================================
    # Domain B: Tempo & Meter [8–16]
    # =========================================================================
    8: ParameterDef(
        id=8, name="BPM", param_type=ParamType.N, tier=Tier.T1, domain=Domain.B,
        values=None, unit="BPM",
    ),
    9: ParameterDef(
        id=9, name="Tempo Feel", param_type=ParamType.O, tier=Tier.T3, domain=Domain.B,
        values=("Adagio", "Andante", "Moderato", "Allegro", "Presto"),
    ),
    10: ParameterDef(
        id=10, name="Tempo Variation", param_type=ParamType.C, tier=Tier.T3, domain=Domain.B,
        values=("Constant", "Accelerando", "Ritardando", "Rubato", "Tempo shifts"),
    ),
    11: ParameterDef(
        id=11, name="Time Signature", param_type=ParamType.C, tier=Tier.T1, domain=Domain.B,
        values=("2/4", "3/4", "4/4", "5/4", "6/8", "7/8", "9/8", "12/8", "Free"),
    ),
    12: ParameterDef(
        id=12, name="Meter Changes", param_type=ParamType.O, tier=Tier.T3, domain=Domain.B,
        values=("None", "Occasional", "Frequent"),
    ),
    13: ParameterDef(
        id=13, name="Beat Subdivision", param_type=ParamType.C, tier=Tier.T3, domain=Domain.B,
        values=("Binary", "Ternary", "Mixed"),
    ),
    14: ParameterDef(
        id=14, name="Swing Amount", param_type=ParamType.N, tier=Tier.T3, domain=Domain.B,
        values=None, unit="%",
    ),
    15: ParameterDef(
        id=15, name="Groove Feel", param_type=ParamType.C, tier=Tier.T1, domain=Domain.B,
        values=("Straight", "Swing", "Shuffle", "Half-time", "Double-time"),
    ),
    16: ParameterDef(
        id=16, name="Pulse Strength", param_type=ParamType.S, tier=Tier.T3, domain=Domain.B,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain C: Rhythm & Groove [17–25]
    # =========================================================================
    17: ParameterDef(
        id=17, name="Rhythmic Density", param_type=ParamType.S, tier=Tier.T2, domain=Domain.C,
        values=("1", "2", "3", "4", "5"),
    ),
    18: ParameterDef(
        id=18, name="Rhythmic Complexity", param_type=ParamType.O, tier=Tier.T2, domain=Domain.C,
        values=("Simple", "Moderate", "Complex", "Polyrhythmic"),
    ),
    19: ParameterDef(
        id=19, name="Syncopation Level", param_type=ParamType.S, tier=Tier.T3, domain=Domain.C,
        values=("1", "2", "3", "4", "5"),
    ),
    20: ParameterDef(
        id=20, name="Percussion Role", param_type=ParamType.O, tier=Tier.T2, domain=Domain.C,
        values=("None", "Minimal", "Standard", "Complex", "Virtuosic"),
    ),
    21: ParameterDef(
        id=21, name="Rhythmic Layering", param_type=ParamType.O, tier=Tier.T3, domain=Domain.C,
        values=("Single", "Dual", "Multi-layer"),
    ),
    22: ParameterDef(
        id=22, name="Polymeter", param_type=ParamType.O, tier=Tier.T3, domain=Domain.C,
        values=("None", "Occasional", "Continuous"),
    ),
    23: ParameterDef(
        id=23, name="Accent Pattern", param_type=ParamType.C, tier=Tier.T3, domain=Domain.C,
        values=("On-beat", "Off-beat", "Syncopated", "Shifting"),
    ),
    24: ParameterDef(
        id=24, name="Groove Intensity", param_type=ParamType.S, tier=Tier.T3, domain=Domain.C,
        values=("1", "2", "3", "4", "5"),
    ),
    25: ParameterDef(
        id=25, name="Rhythmic Ostinato", param_type=ParamType.O, tier=Tier.T3, domain=Domain.C,
        values=("None", "Background", "Structural"),
    ),

    # =========================================================================
    # Domain D: Melody [26–38]
    # =========================================================================
    26: ParameterDef(
        id=26, name="Melodic Presence", param_type=ParamType.C, tier=Tier.T1, domain=Domain.D,
        values=("None (textural)", "Implied", "Clear melody"),
    ),
    27: ParameterDef(
        id=27, name="Melodic Range", param_type=ParamType.C, tier=Tier.T3, domain=Domain.D,
        values=("Narrow (<P8)", "Medium (≈P8)", "Wide (>P8)"),
    ),
    28: ParameterDef(
        id=28, name="Melodic Contour", param_type=ParamType.C, tier=Tier.T2, domain=Domain.D,
        values=("Ascending", "Descending", "Wave", "Arch", "Inverted arch", "Static"),
    ),
    29: ParameterDef(
        id=29, name="Melodic Motion", param_type=ParamType.O, tier=Tier.T3, domain=Domain.D,
        values=("Stepwise", "Mixed", "Leaping"),
    ),
    30: ParameterDef(
        id=30, name="Interval Preference", param_type=ParamType.C, tier=Tier.T3, domain=Domain.D,
        values=("Small (2nds–3rds)", "Mixed", "Wide (6ths+)"),
    ),
    31: ParameterDef(
        id=31, name="Melodic Note Density", param_type=ParamType.S, tier=Tier.T3, domain=Domain.D,
        values=("1", "2", "3", "4", "5"),
    ),
    32: ParameterDef(
        id=32, name="Phrase Length", param_type=ParamType.C, tier=Tier.T3, domain=Domain.D,
        values=("Short (1–2 bars)", "Medium (4)", "Long (8+)"),
    ),
    33: ParameterDef(
        id=33, name="Phrase Symmetry", param_type=ParamType.C, tier=Tier.T3, domain=Domain.D,
        values=("Symmetric", "Asymmetric", "Irregular"),
    ),
    34: ParameterDef(
        id=34, name="Motivic Development", param_type=ParamType.C, tier=Tier.T2, domain=Domain.D,
        values=("Repetition", "Sequence", "Inversion", "Augmentation", "Diminution", "Fragmentation"),
        multi=True,
    ),
    35: ParameterDef(
        id=35, name="Hook Strength", param_type=ParamType.S, tier=Tier.T2, domain=Domain.D,
        values=("1", "2", "3", "4", "5"),
    ),
    36: ParameterDef(
        id=36, name="Ornamentation", param_type=ParamType.O, tier=Tier.T3, domain=Domain.D,
        values=("None", "Subtle", "Moderate", "Rich"),
    ),
    37: ParameterDef(
        id=37, name="Call & Response", param_type=ParamType.O, tier=Tier.T3, domain=Domain.D,
        values=("None", "Occasional", "Structural"),
    ),
    38: ParameterDef(
        id=38, name="Climax Placement", param_type=ParamType.C, tier=Tier.T3, domain=Domain.D,
        values=("Beginning", "Early", "Middle", "Late", "End"),
    ),

    # =========================================================================
    # Domain E: Harmony [39–54]
    # =========================================================================
    39: ParameterDef(
        id=39, name="Harmonic Rhythm", param_type=ParamType.O, tier=Tier.T2, domain=Domain.E,
        values=("Very slow", "Slow", "Medium", "Fast", "Very fast"),
    ),
    40: ParameterDef(
        id=40, name="Chord Type", param_type=ParamType.O, tier=Tier.T2, domain=Domain.E,
        values=("Power chords", "Triads", "7ths", "Extended", "Clusters"),
    ),
    41: ParameterDef(
        id=41, name="Chord Extensions", param_type=ParamType.C, tier=Tier.T3, domain=Domain.E,
        values=("None", "9th", "11th", "13th"), multi=True,
    ),
    42: ParameterDef(
        id=42, name="Suspended/Added Tones", param_type=ParamType.C, tier=Tier.T3, domain=Domain.E,
        values=("None", "sus2", "sus4", "add2", "add6"), multi=True,
    ),
    43: ParameterDef(
        id=43, name="Voicing", param_type=ParamType.C, tier=Tier.T3, domain=Domain.E,
        values=("Closed", "Open", "Drop-2", "Spread"),
    ),
    44: ParameterDef(
        id=44, name="Harmonic Inversion", param_type=ParamType.O, tier=Tier.T3, domain=Domain.E,
        values=("Root only", "Occasional", "Frequent"),
    ),
    45: ParameterDef(
        id=45, name="Progression Type", param_type=ParamType.C, tier=Tier.T1, domain=Domain.E,
        values=("Functional", "Pop loop", "Modal", "Chromatic", "Pedal-based"),
    ),
    46: ParameterDef(
        id=46, name="Progression Length", param_type=ParamType.N, tier=Tier.T2, domain=Domain.E,
        values=("1", "2", "4", "8+"), unit="chords",
    ),
    47: ParameterDef(
        id=47, name="Harmonic Complexity", param_type=ParamType.S, tier=Tier.T2, domain=Domain.E,
        values=("1", "2", "3", "4", "5"),
    ),
    48: ParameterDef(
        id=48, name="Borrowed Chords", param_type=ParamType.O, tier=Tier.T3, domain=Domain.E,
        values=("None", "Occasional", "Frequent"),
    ),
    49: ParameterDef(
        id=49, name="Secondary Dominants", param_type=ParamType.O, tier=Tier.T3, domain=Domain.E,
        values=("None", "Occasional", "Frequent"),
    ),
    50: ParameterDef(
        id=50, name="Dissonance Level", param_type=ParamType.S, tier=Tier.T2, domain=Domain.E,
        values=("1", "2", "3", "4", "5"),
    ),
    51: ParameterDef(
        id=51, name="Resolution Style", param_type=ParamType.O, tier=Tier.T3, domain=Domain.E,
        values=("Immediate", "Delayed", "Suspended", "Unresolved"),
    ),
    52: ParameterDef(
        id=52, name="Pedal Point", param_type=ParamType.C, tier=Tier.T3, domain=Domain.E,
        values=("None", "Tonic", "Dominant", "Moving"),
    ),
    53: ParameterDef(
        id=53, name="Cadence Type", param_type=ParamType.C, tier=Tier.T2, domain=Domain.E,
        values=("Authentic", "Plagal", "Half", "Deceptive", "Evaded"),
    ),
    54: ParameterDef(
        id=54, name="Harmonic Surprise", param_type=ParamType.S, tier=Tier.T3, domain=Domain.E,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain F: Bass [55–59]
    # =========================================================================
    55: ParameterDef(
        id=55, name="Bass Presence", param_type=ParamType.O, tier=Tier.T2, domain=Domain.F,
        values=("None", "Subtle", "Prominent", "Dominant"),
    ),
    56: ParameterDef(
        id=56, name="Bass Movement", param_type=ParamType.C, tier=Tier.T3, domain=Domain.F,
        values=("Static/pedal", "Stepwise", "Root motion", "Leaping"),
    ),
    57: ParameterDef(
        id=57, name="Bass Melodic Independence", param_type=ParamType.O, tier=Tier.T3, domain=Domain.F,
        values=("Root doubling", "Supportive", "Semi-melodic", "Fully melodic"),
    ),
    58: ParameterDef(
        id=58, name="Bass Register", param_type=ParamType.C, tier=Tier.T3, domain=Domain.F,
        values=("Sub-bass", "Low", "Mid-low"),
    ),
    59: ParameterDef(
        id=59, name="Bass Rhythmic Role", param_type=ParamType.C, tier=Tier.T3, domain=Domain.F,
        values=("Sustained", "On-beat", "Syncopated", "Driving"),
    ),

    # =========================================================================
    # Domain G: Texture & Counterpoint [60–66]
    # =========================================================================
    60: ParameterDef(
        id=60, name="Texture Type", param_type=ParamType.C, tier=Tier.T2, domain=Domain.G,
        values=("Monophonic", "Homophonic", "Heterophonic", "Polyphonic"),
    ),
    61: ParameterDef(
        id=61, name="Texture Density", param_type=ParamType.S, tier=Tier.T2, domain=Domain.G,
        values=("1", "2", "3", "4", "5"),
    ),
    62: ParameterDef(
        id=62, name="Layer Count", param_type=ParamType.S, tier=Tier.T3, domain=Domain.G,
        values=("1", "2", "3", "4", "5"),
    ),
    63: ParameterDef(
        id=63, name="Textural Evolution", param_type=ParamType.O, tier=Tier.T3, domain=Domain.G,
        values=("Static", "Gradual", "Sectional", "Frequent shifts"),
    ),
    64: ParameterDef(
        id=64, name="Counterpoint Complexity", param_type=ParamType.O, tier=Tier.T3, domain=Domain.G,
        values=("None", "Simple 2-voice", "Moderate", "Complex", "Fugal"),
    ),
    65: ParameterDef(
        id=65, name="Arpeggio / Figuration", param_type=ParamType.O, tier=Tier.T3, domain=Domain.G,
        values=("None", "Simple", "Complex", "Evolving"),
    ),
    66: ParameterDef(
        id=66, name="Textural Contrast", param_type=ParamType.S, tier=Tier.T3, domain=Domain.G,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain H: Orchestration & Timbre [67–78]
    # =========================================================================
    67: ParameterDef(
        id=67, name="Ensemble Size", param_type=ParamType.O, tier=Tier.T2, domain=Domain.H,
        values=("Solo", "Duo", "Chamber", "Small ensemble", "Orchestra", "Massive"),
    ),
    68: ParameterDef(
        id=68, name="Primary Instrument Family", param_type=ParamType.C, tier=Tier.T1, domain=Domain.H,
        values=("Strings", "Woodwinds", "Brass", "Keys", "Guitar", "Synth", "Percussion", "Vocal", "Mixed"),
        multi=True,
    ),
    69: ParameterDef(
        id=69, name="Lead Instrument Prominence", param_type=ParamType.O, tier=Tier.T3, domain=Domain.H,
        values=("Background", "Balanced", "Dominant"),
    ),
    70: ParameterDef(
        id=70, name="Register Span", param_type=ParamType.C, tier=Tier.T3, domain=Domain.H,
        values=("Low", "Mid", "High", "Full range"),
    ),
    71: ParameterDef(
        id=71, name="Register Contrast", param_type=ParamType.S, tier=Tier.T3, domain=Domain.H,
        values=("1", "2", "3", "4", "5"),
    ),
    72: ParameterDef(
        id=72, name="Timbre Brightness", param_type=ParamType.S, tier=Tier.T2, domain=Domain.H,
        values=("1", "2", "3", "4", "5"),
    ),
    73: ParameterDef(
        id=73, name="Timbre Warmth", param_type=ParamType.S, tier=Tier.T2, domain=Domain.H,
        values=("1", "2", "3", "4", "5"),
    ),
    74: ParameterDef(
        id=74, name="Timbral Variation", param_type=ParamType.O, tier=Tier.T3, domain=Domain.H,
        values=("Static", "Slowly evolving", "Contrasting"),
    ),
    75: ParameterDef(
        id=75, name="Acoustic↔Electronic", param_type=ParamType.O, tier=Tier.T1, domain=Domain.H,
        values=("Acoustic", "Mostly acoustic", "Hybrid", "Mostly electronic", "Electronic"),
    ),
    76: ParameterDef(
        id=76, name="Vintage↔Modern", param_type=ParamType.O, tier=Tier.T2, domain=Domain.H,
        values=("Vintage", "Classic", "Neutral", "Modern", "Futuristic"),
    ),
    77: ParameterDef(
        id=77, name="Primary Articulation", param_type=ParamType.C, tier=Tier.T3, domain=Domain.H,
        values=("Legato", "Portato", "Staccato", "Marcato", "Tenuto", "Pizzicato", "Tremolo"),
    ),
    78: ParameterDef(
        id=78, name="Articulation Variety", param_type=ParamType.S, tier=Tier.T3, domain=Domain.H,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain I: Dynamics & Expression [79–86]
    # =========================================================================
    79: ParameterDef(
        id=79, name="Base Dynamic", param_type=ParamType.O, tier=Tier.T2, domain=Domain.I,
        values=("pp", "p", "mp", "mf", "f", "ff"),
    ),
    80: ParameterDef(
        id=80, name="Dynamic Range", param_type=ParamType.O, tier=Tier.T2, domain=Domain.I,
        values=("Narrow", "Moderate", "Wide", "Extreme"),
    ),
    81: ParameterDef(
        id=81, name="Dynamic Shape", param_type=ParamType.C, tier=Tier.T2, domain=Domain.I,
        values=("Flat", "Gradual swell", "Terraced", "Sudden shifts"),
    ),
    82: ParameterDef(
        id=82, name="Crescendo Span", param_type=ParamType.C, tier=Tier.T3, domain=Domain.I,
        values=("Short", "Medium", "Long", "Section-spanning"),
    ),
    83: ParameterDef(
        id=83, name="Accent Intensity", param_type=ParamType.S, tier=Tier.T3, domain=Domain.I,
        values=("1", "2", "3", "4", "5"),
    ),
    84: ParameterDef(
        id=84, name="Vibrato / Expression Width", param_type=ParamType.O, tier=Tier.T3, domain=Domain.I,
        values=("None", "Subtle", "Moderate", "Wide"),
    ),
    85: ParameterDef(
        id=85, name="Pitch Bend / Glissando", param_type=ParamType.O, tier=Tier.T3, domain=Domain.I,
        values=("None", "Subtle", "Moderate", "Prominent"),
    ),
    86: ParameterDef(
        id=86, name="Humanization", param_type=ParamType.S, tier=Tier.T2, domain=Domain.I,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain J: Form & Structure [87–99]
    # =========================================================================
    87: ParameterDef(
        id=87, name="Overall Form", param_type=ParamType.C, tier=Tier.T2, domain=Domain.J,
        values=("Binary", "Ternary", "Rondo", "Verse-Chorus", "Sonata", "Through-composed", "Strophic", "Free"),
    ),
    88: ParameterDef(
        id=88, name="Duration", param_type=ParamType.N, tier=Tier.T2, domain=Domain.J,
        values=("Short (<2)", "Medium (3–5)", "Long (6–10)", "Extended (10+)"), unit="minutes",
    ),
    89: ParameterDef(
        id=89, name="Section Count", param_type=ParamType.N, tier=Tier.T3, domain=Domain.J,
        values=("Few (2–3)", "Standard (4–6)", "Many (7+)"),
    ),
    90: ParameterDef(
        id=90, name="Section Length", param_type=ParamType.N, tier=Tier.T3, domain=Domain.J,
        values=("Short (4–8)", "Medium (8–16)", "Long (16–32)", "Extended (32+)"), unit="bars",
    ),
    91: ParameterDef(
        id=91, name="Section Contrast", param_type=ParamType.S, tier=Tier.T2, domain=Domain.J,
        values=("1", "2", "3", "4", "5"),
    ),
    92: ParameterDef(
        id=92, name="Intro Style", param_type=ParamType.C, tier=Tier.T2, domain=Domain.J,
        values=("None", "Ambient", "Rhythmic", "Melodic", "Dramatic"),
    ),
    93: ParameterDef(
        id=93, name="Intro Length", param_type=ParamType.O, tier=Tier.T3, domain=Domain.J,
        values=("None", "Short", "Medium", "Extended"),
    ),
    94: ParameterDef(
        id=94, name="Build-up Style", param_type=ParamType.C, tier=Tier.T2, domain=Domain.J,
        values=("None", "Gradual layers", "Rhythmic intensification", "Sudden expansion"),
    ),
    95: ParameterDef(
        id=95, name="Climax Intensity", param_type=ParamType.S, tier=Tier.T2, domain=Domain.J,
        values=("1", "2", "3", "4", "5"),
    ),
    96: ParameterDef(
        id=96, name="Climax Count", param_type=ParamType.O, tier=Tier.T3, domain=Domain.J,
        values=("None", "Single", "Multiple"),
    ),
    97: ParameterDef(
        id=97, name="Bridge/Interlude Function", param_type=ParamType.C, tier=Tier.T3, domain=Domain.J,
        values=("None", "Contrast", "Modulation", "Breakdown", "Solo"),
    ),
    98: ParameterDef(
        id=98, name="Transition Style", param_type=ParamType.C, tier=Tier.T3, domain=Domain.J,
        values=("Cut", "Crossfade", "Fill", "Build", "Ambient link"),
    ),
    99: ParameterDef(
        id=99, name="Ending Style", param_type=ParamType.C, tier=Tier.T2, domain=Domain.J,
        values=("Abrupt", "Fade-out", "Cadential", "Ritardando", "Circular (loops)"),
    ),

    # =========================================================================
    # Domain K: Emotion & Narrative [100–107]
    # =========================================================================
    100: ParameterDef(
        id=100, name="Primary Emotion", param_type=ParamType.C, tier=Tier.T1, domain=Domain.K,
        values=("Joy", "Sadness", "Anger", "Fear", "Serenity", "Wonder", "Tension", "Nostalgia", "Triumph", "Melancholy"),
    ),
    101: ParameterDef(
        id=101, name="Emotional Complexity", param_type=ParamType.O, tier=Tier.T3, domain=Domain.K,
        values=("Single", "Shifting", "Layered/ambiguous"),
    ),
    102: ParameterDef(
        id=102, name="Energy Curve", param_type=ParamType.C, tier=Tier.T2, domain=Domain.K,
        values=("Flat", "Rising", "Falling", "Wave", "Arc"),
    ),
    103: ParameterDef(
        id=103, name="Tension Arc", param_type=ParamType.S, tier=Tier.T2, domain=Domain.K,
        values=("1", "2", "3", "4", "5"),
    ),
    104: ParameterDef(
        id=104, name="Tension–Release Balance", param_type=ParamType.O, tier=Tier.T3, domain=Domain.K,
        values=("Mostly tension", "Balanced", "Mostly release"),
    ),
    105: ParameterDef(
        id=105, name="Narrative Direction", param_type=ParamType.C, tier=Tier.T2, domain=Domain.K,
        values=("Static mood", "Gradual story", "Dramatic arc", "Cyclic"),
    ),
    106: ParameterDef(
        id=106, name="Mood Contrast", param_type=ParamType.S, tier=Tier.T3, domain=Domain.K,
        values=("1", "2", "3", "4", "5"),
    ),
    107: ParameterDef(
        id=107, name="Genre / Cultural Reference", param_type=ParamType.C, tier=Tier.T1, domain=Domain.K,
        values=("Classical", "Jazz", "Rock", "R&B", "Hip-hop", "Metal", "Alternative", "Anatolian Folk", "Cinematic", "None"),
        multi=True,
    ),

    # =========================================================================
    # Domain L: Production & Spatial [108–116]
    # =========================================================================
    108: ParameterDef(
        id=108, name="Spatial Depth", param_type=ParamType.O, tier=Tier.T2, domain=Domain.L,
        values=("Dry/close", "Room", "Hall", "Cathedral", "Cinematic", "Infinite"),
    ),
    109: ParameterDef(
        id=109, name="Stereo Width", param_type=ParamType.O, tier=Tier.T2, domain=Domain.L,
        values=("Mono", "Narrow", "Standard", "Wide", "Ultra-wide"),
    ),
    110: ParameterDef(
        id=110, name="Reverb Amount", param_type=ParamType.S, tier=Tier.T2, domain=Domain.L,
        values=("1", "2", "3", "4", "5"),
    ),
    111: ParameterDef(
        id=111, name="Reverb Type", param_type=ParamType.C, tier=Tier.T3, domain=Domain.L,
        values=("Plate", "Room", "Hall", "Spring", "Shimmer", "Algorithmic"),
    ),
    112: ParameterDef(
        id=112, name="Delay Usage", param_type=ParamType.O, tier=Tier.T3, domain=Domain.L,
        values=("None", "Subtle", "Rhythmic", "Ambient wash"),
    ),
    113: ParameterDef(
        id=113, name="Saturation / Distortion", param_type=ParamType.O, tier=Tier.T3, domain=Domain.L,
        values=("None", "Subtle warmth", "Grit", "Heavy"),
    ),
    114: ParameterDef(
        id=114, name="Filter Movement", param_type=ParamType.O, tier=Tier.T3, domain=Domain.L,
        values=("None", "Static", "Slow sweep", "Rhythmic"),
    ),
    115: ParameterDef(
        id=115, name="Modulation FX", param_type=ParamType.C, tier=Tier.T3, domain=Domain.L,
        values=("None", "Chorus", "Flanger", "Phaser", "Ensemble"), multi=True,
    ),
    116: ParameterDef(
        id=116, name="Production Density", param_type=ParamType.S, tier=Tier.T2, domain=Domain.L,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain M: Vocal [117–120]
    # =========================================================================
    117: ParameterDef(
        id=117, name="Vocal Presence", param_type=ParamType.O, tier=Tier.T1, domain=Domain.M,
        values=("None (instrumental)", "Background", "Featured", "Lead"),
    ),
    118: ParameterDef(
        id=118, name="Vocal Type", param_type=ParamType.C, tier=Tier.T2, domain=Domain.M,
        values=("Soprano", "Alto", "Tenor", "Baritone", "Bass", "Choir", "Mixed"),
    ),
    119: ParameterDef(
        id=119, name="Vocal Style", param_type=ParamType.C, tier=Tier.T2, domain=Domain.M,
        values=("Clean", "Breathy", "Raspy", "Belting", "Whispered", "Falsetto"),
    ),
    120: ParameterDef(
        id=120, name="Vocal Processing", param_type=ParamType.C, tier=Tier.T3, domain=Domain.M,
        values=("Dry", "Light reverb", "Heavy FX", "Vocoder", "Auto-tune"),
    ),

    # =========================================================================
    # Domain N: Lyrics & Prosody [121–129] (v3.0)
    # =========================================================================
    121: ParameterDef(
        id=121, name="Language(s)", param_type=ParamType.C, tier=Tier.T2, domain=Domain.N,
        values=None, multi=True,
    ),
    122: ParameterDef(
        id=122, name="Lyric Density", param_type=ParamType.N, tier=Tier.T2, domain=Domain.N,
        values=None, unit="syllables/bar",
    ),
    123: ParameterDef(
        id=123, name="Rhyme Scheme", param_type=ParamType.C, tier=Tier.T3, domain=Domain.N,
        values=("AABB", "ABAB", "ABCB", "internal", "free verse"),
    ),
    124: ParameterDef(
        id=124, name="Hook Position", param_type=ParamType.C, tier=Tier.T3, domain=Domain.N,
        values=("title-first", "title-last", "every section", "pre-chorus lift"),
    ),
    125: ParameterDef(
        id=125, name="Hook Repetition", param_type=ParamType.N, tier=Tier.T3, domain=Domain.N,
        values=None, unit="times",
    ),
    126: ParameterDef(
        id=126, name="Prosody Fit", param_type=ParamType.S, tier=Tier.T2, domain=Domain.N,
        values=("1", "2", "3", "4", "5"),
    ),
    127: ParameterDef(
        id=127, name="Diction Register", param_type=ParamType.C, tier=Tier.T3, domain=Domain.N,
        values=("Colloquial", "Poetic/literary", "Archaic", "Slang", "Bilingual blend"),
    ),
    128: ParameterDef(
        id=128, name="Syllable–Melody Fit", param_type=ParamType.S, tier=Tier.T3, domain=Domain.N,
        values=("1", "2", "3", "4", "5"),
    ),
    129: ParameterDef(
        id=129, name="Narrative Person", param_type=ParamType.C, tier=Tier.T3, domain=Domain.N,
        values=("1st", "2nd", "3rd", "shifting"),
    ),

    # =========================================================================
    # Domain O: Structure Timeline [130–134] (v3.0)
    # =========================================================================
    130: ParameterDef(
        id=130, name="Section Map", param_type=ParamType.T, tier=Tier.T2, domain=Domain.O,
        values=None,
    ),
    131: ParameterDef(
        id=131, name="Per-Section Energy", param_type=ParamType.T, tier=Tier.T2, domain=Domain.O,
        values=None,
    ),
    132: ParameterDef(
        id=132, name="Instrument Entry/Exit Map", param_type=ParamType.T, tier=Tier.T3, domain=Domain.O,
        values=None,
    ),
    133: ParameterDef(
        id=133, name="Event Markers", param_type=ParamType.T, tier=Tier.T3, domain=Domain.O,
        values=None,
    ),
    134: ParameterDef(
        id=134, name="Total Bars", param_type=ParamType.N, tier=Tier.T2, domain=Domain.O,
        values=None, unit="bars",
    ),

    # =========================================================================
    # Domain P: Exclusions [135–138] (v3.0)
    # =========================================================================
    135: ParameterDef(
        id=135, name="Avoid List", param_type=ParamType.C, tier=Tier.T2, domain=Domain.P,
        values=("risers", "trap hats", "autotune", "guitar solos", "key change", "spoken word"),
        multi=True,
    ),
    136: ParameterDef(
        id=136, name="Forbidden Instruments", param_type=ParamType.C, tier=Tier.T3, domain=Domain.P,
        values=None, multi=True,
    ),
    137: ParameterDef(
        id=137, name="Cliché Avoidance", param_type=ParamType.S, tier=Tier.T3, domain=Domain.P,
        values=("1", "2", "3", "4", "5"),
    ),
    138: ParameterDef(
        id=138, name="Mix Exclusions", param_type=ParamType.C, tier=Tier.T3, domain=Domain.P,
        values=("no sidechain pump", "no sub-drop", "no gated reverb"), multi=True,
    ),

    # =========================================================================
    # Domain Q: Reference Anchors [139–143] (v3.0)
    # =========================================================================
    139: ParameterDef(
        id=139, name="Anchors", param_type=ParamType.C, tier=Tier.T2, domain=Domain.Q,
        values=None, multi=True,
    ),
    140: ParameterDef(
        id=140, name="Production Era", param_type=ParamType.O, tier=Tier.T3, domain=Domain.Q,
        values=("70s tape", "90s digital", "Modern hi-fi", "Lo-fi"),
    ),
    141: ParameterDef(
        id=141, name="Regional/Traditional Reference", param_type=ParamType.C, tier=Tier.T3, domain=Domain.Q,
        values=("Turkish", "Persian", "Balkan", "Appalachian", "None"),
    ),
    142: ParameterDef(
        id=142, name="Anchor Delta", param_type=ParamType.T, tier=Tier.T3, domain=Domain.Q,
        values=None,
    ),
    143: ParameterDef(
        id=143, name="Novelty↔Familiarity", param_type=ParamType.S, tier=Tier.T3, domain=Domain.Q,
        values=("1", "2", "3", "4", "5"),
    ),

    # =========================================================================
    # Domain R: Mix & Arrangement [144–148] (v3.0)
    # =========================================================================
    144: ParameterDef(
        id=144, name="Stem Priority", param_type=ParamType.C, tier=Tier.T2, domain=Domain.R,
        values=("drums", "bass", "lead vocal", "pad", "rhythm guitar", "lead synth", "saz/bağlama"),
        multi=True,
    ),
    145: ParameterDef(
        id=145, name="Loudness Target", param_type=ParamType.N, tier=Tier.T3, domain=Domain.R,
        values=("-14", "-16", "-24"), unit="LUFS",
    ),
    146: ParameterDef(
        id=146, name="Reference Track", param_type=ParamType.C, tier=Tier.T3, domain=Domain.R,
        values=None,
    ),
    147: ParameterDef(
        id=147, name="Arrangement Note", param_type=ParamType.C, tier=Tier.T3, domain=Domain.R,
        values=None,
    ),
    148: ParameterDef(
        id=148, name="Version Variants", param_type=ParamType.C, tier=Tier.T3, domain=Domain.R,
        values=("radio edit", "extended", "instrumental", "acapella", "stem pack", "Reels cut (≤90 s)"),
        multi=True,
    ),

    # =========================================================================
    # Domain S: AI Generator Directives [149–154] (v3.0)
    # =========================================================================
    149: ParameterDef(
        id=149, name="Negative Prompt", param_type=ParamType.C, tier=Tier.T2, domain=Domain.S,
        values=None, multi=True,
    ),
    150: ParameterDef(
        id=150, name="Anchor Weight", param_type=ParamType.N, tier=Tier.T3, domain=Domain.S,
        values=None,
    ),
    151: ParameterDef(
        id=151, name="Seed", param_type=ParamType.N, tier=Tier.T3, domain=Domain.S,
        values=None,
    ),
    152: ParameterDef(
        id=152, name="Generation Mode", param_type=ParamType.C, tier=Tier.T3, domain=Domain.S,
        values=("text-to-music", "extend", "inpaint", "remix", "cover"),
    ),
    153: ParameterDef(
        id=153, name="Prompt Verbosity", param_type=ParamType.O, tier=Tier.T3, domain=Domain.S,
        values=("keywords-only", "standard", "detailed", "verbose"),
    ),
    154: ParameterDef(
        id=154, name="Iteration Budget", param_type=ParamType.N, tier=Tier.T3, domain=Domain.S,
        values=None,
    ),

    # =========================================================================
    # Domain T: Project & Release Context [155–160] (v3.0)
    # =========================================================================
    155: ParameterDef(
        id=155, name="Release Platform", param_type=ParamType.C, tier=Tier.T2, domain=Domain.T,
        values=("SoundCloud", "Spotify", "Instagram Reels", "YouTube Shorts", "TikTok", "Bandcamp"),
        multi=True,
    ),
    156: ParameterDef(
        id=156, name="CRM Tag", param_type=ParamType.C, tier=Tier.T3, domain=Domain.T,
        values=None,
    ),
    157: ParameterDef(
        id=157, name="Monetization Priority", param_type=ParamType.C, tier=Tier.T3, domain=Domain.T,
        values=("sync licensing", "streaming", "live", "merch", "pre-sell/SFS"),
    ),
    158: ParameterDef(
        id=158, name="Target Duration", param_type=ParamType.N, tier=Tier.T3, domain=Domain.T,
        values=None, unit="seconds",
    ),
    159: ParameterDef(
        id=159, name="Campaign Phase", param_type=ParamType.C, tier=Tier.T3, domain=Domain.T,
        values=("teaser", "release-day", "push", "evergreen", "archive"),
    ),
    160: ParameterDef(
        id=160, name="Language Market", param_type=ParamType.C, tier=Tier.T3, domain=Domain.T,
        values=("TR-primary", "IR-primary", "EN-primary", "diaspora-TR", "diaspora-IR", "multi"),
    ),
}
