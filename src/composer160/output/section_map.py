"""Section Map and Temporal Structure Logic (Domain O).

Models musical sections with bar counts and energy dynamics, translating
overall song forms into discrete temporal sequences.
"""

from dataclasses import dataclass
import re
from typing import Sequence

from composer160.core.vector import ParameterVector

# Circled numeric symbols for per-section energy ratings ① through ⑤
CIRCLED_ENERGIES: dict[int, str] = {
    1: "①",
    2: "②",
    3: "③",
    4: "④",
    5: "⑤",
}


@dataclass
class Section:
    """A discrete temporal segment in the song arrangement."""

    name: str
    bars: int
    energy: int  # 1 through 5


class SectionMapBuilder:
    """Calculates and formats musical section timelines and energy curves."""

    def build_from_vector(self, vec: ParameterVector) -> list[Section]:
        """Derive an ordered list of Section instances from a ParameterVector."""
        raw_map = vec.get(130)
        raw_energies = vec.get(131)

        # 1. If explicit Section Map (#130) is present as list of tuples/dicts
        if isinstance(raw_map, (list, tuple)) and raw_map:
            energies_list: list[int] = []
            if isinstance(raw_energies, (list, tuple)):
                energies_list = [int(e) for e in raw_energies]

            sections: list[Section] = []
            for i, item in enumerate(raw_map):
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    name = str(item[0])
                    bars = int(item[1])
                elif isinstance(item, dict):
                    name = str(item.get("name", f"Section {i+1}"))
                    bars = int(item.get("bars", 8))
                else:
                    name = str(item)
                    bars = 8

                energy = energies_list[i] if i < len(energies_list) else self._default_section_energy(name)
                sections.append(Section(name=name, bars=bars, energy=energy))
            return sections

        # 2. If Section Map (#130) is stored as a formatted timeline string
        if isinstance(raw_map, str) and raw_map != "auto":
            # Matches tokens like "Intro8", "V16", "Pre8", "Ch16"
            tokens = re.split(r"[·•\s,]+", raw_map.strip())
            sections = []
            for token in tokens:
                match = re.match(r"^([A-Za-z\s]+?)(\d+)$", token.strip())
                if match:
                    name = match.group(1).strip()
                    bars = int(match.group(2))
                    energy = self._default_section_energy(name)
                    sections.append(Section(name=name, bars=bars, energy=energy))
            if sections:
                return sections

        # 3. Derive standard section map from Form (#87) and Total Bars (#134)
        form = vec.get(87)
        total_bars_val = vec.get(134)
        total_bars = int(total_bars_val) if (total_bars_val != "auto" and total_bars_val) else 75

        return self._generate_form_sections(form, total_bars)

    def format_map(self, sections: Sequence[Section]) -> str:
        """Render a concise timeline string e.g. 'Intro4 · V12 · Pre4 · Ch12 · Outro7'."""
        formatted_parts: list[str] = []
        for s in sections:
            abbrev = self._abbreviate_name(s.name)
            formatted_parts.append(f"{abbrev}{s.bars}")
        return " · ".join(formatted_parts)

    def format_energy(self, sections: Sequence[Section]) -> str:
        """Render a circled energy progression string e.g. '②·③·④·⑤·③·④·⑤·③·①'."""
        energy_chars = [CIRCLED_ENERGIES.get(max(1, min(5, s.energy)), "③") for s in sections]
        return "·".join(energy_chars)

    def _default_section_energy(self, name: str) -> int:
        """Provide typical energy levels by section function."""
        lower = name.lower()
        if "intro" in lower:
            return 2
        if "verse" in lower or lower.startswith("v"):
            return 3
        if "pre" in lower:
            return 4
        if "chorus" in lower or "ch" in lower or "hook" in lower:
            return 5
        if "bridge" in lower or "br" in lower:
            return 3
        if "solo" in lower:
            return 4
        if "outro" in lower:
            return 1
        return 3

    def _abbreviate_name(self, name: str) -> str:
        """Convert verbose section names to clean timeline abbreviations.

        Matches canonical spec notation: V16, Ch16, Pre8, Br16, Intro8, Outro8.
        """
        lower = name.lower()
        if "intro" in lower:
            return "Intro"
        if "pre" in lower:
            return "Pre"
        if "chorus" in lower or lower.startswith("ch") or "hook" in lower:
            return "Ch"
        if "verse" in lower or lower.startswith("v"):
            return "V"
        if "bridge" in lower or lower.startswith("br"):
            return "Br"
        if "solo" in lower:
            return "Solo"
        if "outro" in lower:
            return "Outro"
        return name

    def _generate_form_sections(self, form: str, total_bars: int) -> list[Section]:
        """Generate a proportional section distribution based on the musical form."""
        if form == "Through-composed":
            count = 5
            bars_each = total_bars // count
            rem = total_bars % count
            return [
                Section("Part 1", bars_each, 2),
                Section("Part 2", bars_each, 3),
                Section("Part 3", bars_each, 4),
                Section("Part 4", bars_each, 5),
                Section("Part 5", bars_each + rem, 2),
            ]

        if form == "AABA" or form == "Ternary":
            a_bars = total_bars // 4
            b_bars = total_bars - (3 * a_bars)
            return [
                Section("A1", a_bars, 3),
                Section("A2", a_bars, 4),
                Section("B", b_bars, 5),
                Section("A3", a_bars, 3),
            ]

        # Default Verse-Chorus standard
        proportions = [
            ("Intro", 4, 2),
            ("Verse 1", 12, 3),
            ("Pre-Chorus", 4, 4),
            ("Chorus 1", 12, 5),
            ("Verse 2", 12, 3),
            ("Pre-Chorus 2", 4, 4),
            ("Chorus 2", 12, 5),
            ("Bridge", 8, 3),
            ("Outro", 7, 1),
        ]
        base_sum = sum(p[1] for p in proportions)

        if total_bars == base_sum:
            return [Section(name=p[0], bars=p[1], energy=p[2]) for p in proportions]

        scale = total_bars / base_sum
        scaled_sections: list[Section] = []
        allocated = 0
        for i, p in enumerate(proportions):
            if i == len(proportions) - 1:
                bars = total_bars - allocated
            else:
                bars = max(2, int(round(p[1] * scale)))
                allocated += bars
            scaled_sections.append(Section(name=p[0], bars=bars, energy=p[2]))

        return scaled_sections
