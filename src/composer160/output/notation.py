"""Compact Bracket Vector Notation Renderer (§5).

Renders a ParameterVector into the canonical COMPOSER-160 bracketed syntax,
ordering T1 parameters first, followed by T2, and omitting auto parameters.
"""

from composer160.core.parameters import PARAMETER_REGISTRY
from composer160.core.types import Tier
from composer160.core.vector import ParameterVector
from composer160.output.section_map import CIRCLED_ENERGIES, SectionMapBuilder


def render_vector(vec: ParameterVector) -> str:
    """Render a ParameterVector into the standard compact bracket notation.

    Produces lines of bracketed tags ordered by tier (T1 -> T2 -> active T3).
    Omit anything left at auto.
    """
    lines: list[str] = []

    # =========================================================================
    # Block 1: T1 Tonal, Tempo & Groove Foundation
    # =========================================================================
    block1: list[str] = []
    root_key = vec.get(1)
    tonality = vec.get(2)
    mode = vec.get(3)

    if root_key != "auto" and root_key:
        key_suffix = "m" if tonality == "Minor" else ""
        block1.append(f"[KEY:{root_key}{key_suffix}]")

    if tonality != "auto" and tonality:
        ton_str = tonality
        if mode != "auto" and mode:
            ton_str = f"{tonality}/{mode}"
        block1.append(f"[TONALITY:{ton_str}]")

    bpm = vec.get(8)
    if bpm != "auto" and bpm:
        block1.append(f"[BPM:{bpm}]")

    time_sig = vec.get(11)
    if time_sig != "auto" and time_sig:
        block1.append(f"[TIMESIG:{time_sig}]")

    groove = vec.get(15)
    if groove != "auto" and groove:
        block1.append(f"[GROOVE:{groove}]")

    if block1:
        lines.append("".join(block1))

    # =========================================================================
    # Block 2: T1 Melodic, Progression & Orchestration Foundation
    # =========================================================================
    block2: list[str] = []
    melody = vec.get(26)
    if melody != "auto" and melody:
        mel_str = "Clear" if "Clear" in str(melody) else str(melody)
        block2.append(f"[MELODY:{mel_str}]")

    prog = vec.get(45)
    if prog != "auto" and prog:
        block2.append(f"[PROG:{prog}]")

    ensemble = vec.get(67)
    if ensemble != "auto" and ensemble:
        block2.append(f"[ENSEMBLE:{ensemble}]")

    aex = vec.get(75)
    if aex != "auto" and aex:
        block2.append(f"[AEX:{aex}]")

    if block2:
        lines.append("".join(block2))

    # =========================================================================
    # Block 3: T1 Emotion, Genre & Vocal Foundation
    # =========================================================================
    block3: list[str] = []
    emotion = vec.get(100)
    if emotion != "auto" and emotion:
        block3.append(f"[EMOTION:{emotion}]")

    genre = vec.get(107)
    if genre != "auto" and genre:
        if isinstance(genre, (list, tuple)):
            genre_str = "+".join(str(g) for g in genre if str(g).lower() != "none")
        else:
            genre_str = str(genre)
        block3.append(f"[GENRE:{genre_str}]")

    vocal_presence = vec.get(117)
    if vocal_presence != "auto" and vocal_presence:
        vocal_style = vec.get(119)
        vocal_type = vec.get(118)
        v_parts = [str(vocal_presence)]
        if vocal_style != "auto" and vocal_style:
            v_parts.append(str(vocal_style))
        elif vocal_type != "auto" and vocal_type:
            v_parts.append(str(vocal_type))
        block3.append(f"[VOCAL:{'·'.join(v_parts)}]")

    if block3:
        lines.append("".join(block3))

    # =========================================================================
    # Block 4: T2 Lyrics & Prosody
    # =========================================================================
    block4: list[str] = []
    lang = vec.get(121)
    if lang != "auto" and lang:
        lang_str = "/".join(str(l) for l in lang) if isinstance(lang, (list, tuple)) else str(lang)
        block4.append(f"[LANG:{lang_str}]")

    prosody = vec.get(126)
    if prosody != "auto" and isinstance(prosody, (int, float)):
        p_symbol = CIRCLED_ENERGIES.get(int(prosody), str(prosody))
        block4.append(f"[PROSODY:{p_symbol}]")

    hook_pos = vec.get(124)
    hook_rep = vec.get(125)
    if hook_pos != "auto" and hook_pos:
        hook_str = str(hook_pos)
        if hook_rep != "auto" and hook_rep:
            hook_str += f"×{hook_rep}"
        block4.append(f"[HOOK:{hook_str}]")

    if block4:
        lines.append("".join(block4))

    # =========================================================================
    # Block 5: Structure Timeline & Energy Map (Domain O)
    # =========================================================================
    builder = SectionMapBuilder()
    sections = builder.build_from_vector(vec)
    if sections:
        map_str = builder.format_map(sections)
        energy_str = builder.format_energy(sections)
        lines.append(f"[MAP:{map_str}]")
        lines.append(f"[ENERGY:{energy_str}]")

    # =========================================================================
    # Block 6: Reference Anchors & Exclusions
    # =========================================================================
    anchors = vec.get(139)
    if anchors != "auto" and anchors:
        if isinstance(anchors, (list, tuple)):
            anc_str = "·".join(str(a) for a in anchors)
        else:
            anc_str = str(anchors).replace(" + ", "·")
        lines.append(f"[ANCHORS:{anc_str}]")

    neg = vec.get(149)
    if neg != "auto" and neg:
        if isinstance(neg, (list, tuple)):
            neg_items = [str(x).replace(" ", "-") for x in neg[:5]]
            neg_str = "·".join(neg_items)
        else:
            neg_str = str(neg).replace(", ", "·").replace(" ", "-")
        lines.append(f"[NEG:{neg_str}]")

    # =========================================================================
    # Block 7: Platform & Release Context
    # =========================================================================
    block7: list[str] = []
    platform = vec.get(155)
    if platform != "auto" and platform:
        if isinstance(platform, (list, tuple)):
            plat_str = "·".join(str(p) for p in platform)
        else:
            plat_str = str(platform)
        block7.append(f"[PLATFORM:{plat_str}]")

    phase = vec.get(159)
    if phase != "auto" and phase:
        block7.append(f"[PHASE:{phase}]")

    market = vec.get(160)
    if market != "auto" and market:
        block7.append(f"[MARKET:{market}]")

    if block7:
        lines.append("".join(block7))

    return "\n".join(lines)
