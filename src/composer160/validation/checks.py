"""COMPOSER-160 Validation Engine.

Implements the C1–C7 self-checks enforcing musical consistency,
topological validity, duration math, and exclusion coverage.
"""

from dataclasses import dataclass
import re
from typing import Any, Sequence

from composer160.core import PARAMETER_REGISTRY, ParameterVector
from composer160.core.parameters import T1_PARAMETER_IDS


@dataclass
class CheckResult:
    """Outcome of a single consistency self-check."""

    check_id: str
    passed: bool
    message: str
    auto_fixed: bool = False
    fix_description: str | None = None


class Validator:
    """Validates a ParameterVector against canonical COMPOSER-160 constraints."""

    def validate(self, vec: ParameterVector) -> list[CheckResult]:
        """Execute all C1 through C7 self-checks in strict priority sequence."""
        return [
            self._c1_tier_completeness(vec),
            self._c2_tonality_topology(vec),
            self._c3_length_chain(vec),
            self._c4_energy_coherence(vec),
            self._c5_vocal_chain(vec),
            self._c6_map_arithmetic(vec),
            self._c7_exclusion_coverage(vec),
        ]

    def _c1_tier_completeness(self, vec: ParameterVector) -> CheckResult:
        """C1 · Tier completeness: all 12 T1 fields present and non-contradictory."""
        missing_ids = [pid for pid in T1_PARAMETER_IDS if not vec.is_set(pid)]
        if missing_ids:
            missing_names = [
                PARAMETER_REGISTRY[pid].name if pid in PARAMETER_REGISTRY else f"#{pid}"
                for pid in missing_ids
            ]
            return CheckResult(
                check_id="C1",
                passed=False,
                message=f"Missing {len(missing_ids)} non-negotiable T1 field(s): {', '.join(missing_names)}",
            )
        return CheckResult(
            check_id="C1",
            passed=True,
            message="All 12 T1 parameters are populated.",
        )

    def _c2_tonality_topology(self, vec: ParameterVector) -> CheckResult:
        """C2 · Tonality topology: Modal requires #3 Mode; Atonal forbids #3, #45 functional/modal, and #53 cadences."""
        tonality = vec.get(2)
        mode = vec.get(3)
        progression = vec.get(45)
        cadence = vec.get(53)

        violations: list[str] = []

        if tonality == "Atonal":
            if mode != "auto" and mode is not None:
                violations.append("Atonal tonality forbids #3 Mode")
            if progression in ("Functional", "Modal"):
                violations.append(f"Atonal tonality forbids {progression} progression in #45")
            if cadence != "auto" and cadence not in (None, "None"):
                violations.append(f"Atonal tonality forbids cadences (#53={cadence})")

        elif tonality == "Modal":
            if mode == "auto" or mode is None:
                violations.append("Modal tonality requires #3 Mode to be explicitly specified")

        if violations:
            return CheckResult(
                check_id="C2",
                passed=False,
                message="; ".join(violations),
            )

        return CheckResult(
            check_id="C2",
            passed=True,
            message="Tonality topology is consistent.",
        )

    def _c3_length_chain(self, vec: ParameterVector) -> CheckResult:
        """C3 · Length chain: #88 Duration ↔ #134 Total Bars ↔ #158 agree within ±5% at stated BPM."""
        bpm = vec.get(8)
        time_sig = vec.get(11)
        duration_cat = vec.get(88)
        total_bars = vec.get(134)
        target_dur_sec = vec.get(158)

        if (
            bpm == "auto"
            or total_bars == "auto"
            or not isinstance(bpm, (int, float))
            or not isinstance(total_bars, (int, float))
            or bpm <= 0
            or total_bars <= 0
        ):
            return CheckResult(
                check_id="C3",
                passed=True,
                message="Length chain: skipped or auto (BPM or Total Bars not numeric).",
            )

        # Calculate seconds per bar based on time signature
        quarter_beats_per_bar = 4.0
        if isinstance(time_sig, str) and "/" in time_sig:
            try:
                num_str, denom_str = time_sig.strip().split("/", 1)
                quarter_beats_per_bar = float(num_str) * (4.0 / float(denom_str))
            except ValueError:
                quarter_beats_per_bar = 4.0

        bar_seconds = quarter_beats_per_bar * (60.0 / float(bpm))
        calculated_seconds = float(total_bars) * bar_seconds

        # Cross-check with Target Duration (#158) in seconds if specified
        if (
            target_dur_sec != "auto"
            and isinstance(target_dur_sec, (int, float))
            and target_dur_sec > 0
        ):
            deviation = abs(calculated_seconds - float(target_dur_sec)) / float(target_dur_sec)
            if deviation > 0.05:
                return CheckResult(
                    check_id="C3",
                    passed=False,
                    message=(
                        f"Calculated length ({calculated_seconds:.1f}s from {total_bars} bars @ {bpm} BPM) "
                        f"deviates from #158 Target Duration ({target_dur_sec:.1f}s) by {deviation:.1%} (>5% threshold)"
                    ),
                )

        # Cross-check with #88 Duration category if specified
        if isinstance(duration_cat, str) and duration_cat != "auto":
            # Categorical boundaries in seconds (with 15% tolerance)
            cat_ranges = {
                "Short (<2)": (0, 140),
                "Medium (3–5)": (150, 345),
                "Medium (3-5)": (150, 345),
                "Long (6–10)": (310, 690),
                "Extended (10+)": (550, 10000),
            }
            if duration_cat in cat_ranges:
                min_sec, max_sec = cat_ranges[duration_cat]
                if not (min_sec <= calculated_seconds <= max_sec):
                    return CheckResult(
                        check_id="C3",
                        passed=False,
                        message=(
                            f"Calculated duration ({calculated_seconds:.1f}s) is inconsistent with "
                            f"#88 Duration category '{duration_cat}'"
                        ),
                    )

        return CheckResult(
            check_id="C3",
            passed=True,
            message=f"Length chain consistent: {total_bars} bars @ {bpm} BPM = {calculated_seconds:.1f}s.",
        )

    def _c4_energy_coherence(self, vec: ParameterVector) -> CheckResult:
        """C4 · Energy coherence: #102 curve, #103 arc, #95 climax, and #131 section energies tell one coherent story."""
        curve = vec.get(102)
        tension = vec.get(103)
        climax = vec.get(95)
        section_energies = vec.get(131)

        # Evaluate energy list against curve
        if isinstance(section_energies, Sequence) and len(section_energies) >= 2:
            try:
                num_energies = [float(e) for e in section_energies]
                max_e = max(num_energies)
                peak_idx = num_energies.index(max_e)
                peak_ratio = peak_idx / (len(num_energies) - 1)

                if curve == "Rising" and peak_ratio < 0.25:
                    return CheckResult(
                        check_id="C4",
                        passed=False,
                        message=f"Rising energy curve conflicts with peak energy in the opening section ({peak_ratio:.1%}).",
                    )
                if curve == "Falling" and peak_ratio > 0.75:
                    return CheckResult(
                        check_id="C4",
                        passed=False,
                        message=f"Falling energy curve conflicts with peak energy at the track conclusion ({peak_ratio:.1%}).",
                    )
                if curve == "Flat" and (max(num_energies) - min(num_energies) > 2.0):
                    return CheckResult(
                        check_id="C4",
                        passed=False,
                        message="Flat energy curve conflicts with excessive section energy variance (>2.0 delta).",
                    )
            except (ValueError, TypeError):
                pass

        # Evaluate tension arc vs climax intensity extremes
        if isinstance(tension, (int, float)) and isinstance(climax, (int, float)):
            if tension <= 1 and climax >= 5:
                return CheckResult(
                    check_id="C4",
                    passed=False,
                    message=f"Tension Arc={tension} (constant low) contradicts Climax Intensity={climax} (epic).",
                )
            if tension >= 5 and climax <= 1:
                return CheckResult(
                    check_id="C4",
                    passed=False,
                    message=f"Tension Arc={tension} (extreme build-release) contradicts Climax Intensity={climax} (subtle peak).",
                )

        return CheckResult(
            check_id="C4",
            passed=True,
            message="Energy curve, tension arc, and section energies are coherent.",
        )

    def _c5_vocal_chain(self, vec: ParameterVector) -> CheckResult:
        """C5 · Vocal chain: #117 ≠ None requires #121 Language and #119 Style; non-English requires #126 Prosody ≥ 3."""
        vocal_presence = vec.get(117)
        if vocal_presence in ("None (instrumental)", "auto", None):
            return CheckResult(
                check_id="C5",
                passed=True,
                message="Instrumental track — vocal chain requirements satisfied.",
            )

        issues: list[str] = []
        language = vec.get(121)
        vocal_style = vec.get(119)
        prosody = vec.get(126)

        if language == "auto" or not language:
            issues.append("Vocal presence requires #121 Language(s) to be set")
        if vocal_style == "auto" or not vocal_style:
            issues.append("Vocal presence requires #119 Vocal Style to be set")

        # Non-English prosody requirement
        if language != "auto" and language:
            lang_repr = str(language).upper()
            is_purely_english = lang_repr in ("['EN']", "['ENGLISH']", "EN", "ENGLISH")
            if not is_purely_english:
                if prosody != "auto" and isinstance(prosody, (int, float)) and prosody < 3:
                    issues.append(
                        f"Non-English vocal ({language}) requires Prosody Fit #126 >= 3 to prevent unsingable output (got {prosody})"
                    )

        if issues:
            return CheckResult(
                check_id="C5",
                passed=False,
                message="; ".join(issues),
            )

        return CheckResult(
            check_id="C5",
            passed=True,
            message="Vocal chain consistent (presence, style, language, and prosody aligned).",
        )

    def _c6_map_arithmetic(self, vec: ParameterVector) -> CheckResult:
        """C6 · Map arithmetic: total bars in #130 must equal #134 exactly."""
        section_map = vec.get(130)
        total_bars = vec.get(134)

        if section_map == "auto" or total_bars == "auto" or total_bars is None:
            return CheckResult(
                check_id="C6",
                passed=True,
                message="Map arithmetic: skipped (Section Map or Total Bars unset).",
            )

        sum_bars = 0

        # Handle list of tuples or lists: [("Intro", 8), ("Verse 1", 16), ...]
        if isinstance(section_map, (list, tuple)):
            for item in section_map:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    try:
                        sum_bars += int(item[1])
                    except (ValueError, TypeError):
                        pass
                elif isinstance(item, dict) and "bars" in item:
                    try:
                        sum_bars += int(item["bars"])
                    except (ValueError, TypeError):
                        pass

        # Handle string format: "Intro8 · V16 · Pre8 · Ch16 · Outro8"
        elif isinstance(section_map, str):
            digits = re.findall(r"\b[A-Za-z]+(\d+)\b", section_map)
            sum_bars = sum(int(d) for d in digits)

        try:
            expected_bars = int(total_bars)
            if sum_bars != expected_bars:
                return CheckResult(
                    check_id="C6",
                    passed=False,
                    message=f"Section map sums to {sum_bars} bars, but #134 Total Bars specifies {expected_bars} bars",
                )
        except (ValueError, TypeError):
            pass

        return CheckResult(
            check_id="C6",
            passed=True,
            message=f"Map arithmetic valid: section map sums exactly to {total_bars} bars.",
        )

    def _c7_exclusion_coverage(self, vec: ParameterVector) -> CheckResult:
        """C7 · Exclusion coverage: every #135–#138 entry appears in the negative prompt (#149), nowhere in positive prompt."""
        avoid_list = vec.get(135)
        forbidden_instruments = vec.get(136)
        mix_exclusions = vec.get(138)
        negative_prompt = vec.get(149)

        # Collect all specified exclusions
        raw_exclusions: list[str] = []
        for src in (avoid_list, forbidden_instruments, mix_exclusions):
            if src != "auto" and src is not None:
                if isinstance(src, (list, tuple, set)):
                    raw_exclusions.extend(str(item).strip().lower() for item in src)
                elif isinstance(src, str):
                    raw_exclusions.append(src.strip().lower())

        if not raw_exclusions:
            return CheckResult(
                check_id="C7",
                passed=True,
                message="No negative exclusions specified.",
            )

        # Collect negative prompt tokens
        neg_items: list[str] = []
        if negative_prompt != "auto" and negative_prompt is not None:
            if isinstance(negative_prompt, (list, tuple, set)):
                neg_items = [str(item).strip().lower() for item in negative_prompt]
            elif isinstance(negative_prompt, str):
                neg_items = [part.strip().lower() for part in negative_prompt.split(",")]

        neg_text = " ".join(neg_items)

        # Verify coverage: each exclusion should be matched in negative prompt
        uncovered: list[str] = []
        for excl in raw_exclusions:
            # Clean string for substring/token matching
            clean_excl = excl.replace("no ", "").strip()
            # If not in negative prompt text
            if clean_excl not in neg_text and excl not in neg_text:
                uncovered.append(excl)

        # Verify no forbidden instrument is in positive arrangement/stems
        positive_stems = vec.get(144)
        positive_instruments = vec.get(68)
        positive_items: list[str] = []
        for p_src in (positive_stems, positive_instruments):
            if p_src != "auto" and p_src is not None:
                if isinstance(p_src, (list, tuple, set)):
                    positive_items.extend(str(x).strip().lower() for x in p_src)
                elif isinstance(p_src, str):
                    positive_items.append(p_src.strip().lower())

        leaks: list[str] = []
        if forbidden_instruments != "auto" and forbidden_instruments:
            forbidden_list = (
                forbidden_instruments
                if isinstance(forbidden_instruments, (list, tuple))
                else [forbidden_instruments]
            )
            for f_inst in forbidden_list:
                f_name = str(f_inst).strip().lower()
                for pos in positive_items:
                    if f_name in pos:
                        leaks.append(f_inst)

        if leaks:
            return CheckResult(
                check_id="C7",
                passed=False,
                message=f"Forbidden instrument(s) leaked into positive arrangement: {', '.join(leaks)}",
            )

        if uncovered:
            return CheckResult(
                check_id="C7",
                passed=False,
                message=f"Exclusion item(s) not covered in #149 Negative Prompt: {', '.join(uncovered)}",
            )

        return CheckResult(
            check_id="C7",
            passed=True,
            message="All exclusions and forbidden elements are covered in the negative prompt.",
        )
