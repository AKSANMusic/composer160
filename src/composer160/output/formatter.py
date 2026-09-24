"""Composer Output Formatter.

Encapsulates the complete response contract from COMPOSER-160, including
the parameter vector, compact notation, Suno/Lyria prompts, section timeline,
assumptions notes, and C1–C7 validation diagnostics.
"""

from dataclasses import asdict, dataclass
import json
from typing import Any

from composer160.core.vector import ParameterVector
from composer160.generators.lyria import LyriaOutput
from composer160.generators.suno import SunoOutput
from composer160.validation.checks import CheckResult


@dataclass
class ComposerOutput:
    """The unified, multi-generator musical direction package."""

    vector: ParameterVector
    compact: str
    suno: SunoOutput
    lyria: LyriaOutput
    section_map: str
    assumptions: list[str]
    checks: list[CheckResult]

    def to_dict(self) -> dict[str, Any]:
        """Convert output to a clean serializable dictionary."""
        return {
            "suno": {
                "style_prompt": self.suno.style_prompt,
                "exclude_styles": self.suno.exclude_styles,
                "lyrics": self.suno.lyrics,
            },
            "lyria": {
                "narrative_prompt": self.lyria.narrative_prompt,
                "lyrics": self.lyria.lyrics,
            },
            "compact_vector": self.compact,
            "section_map": self.section_map,
            "assumptions": self.assumptions,
            "validation": [
                {
                    "check_id": c.check_id,
                    "passed": c.passed,
                    "message": c.message,
                }
                for c in self.checks
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize output to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Render the official dual-engine markdown response."""
        md_lines: list[str] = [
            "### 1. SUNO ENGINE OUTPUT (Structured & Tag-Based)",
            "**Style Prompt:**",
            f"> `{self.suno.style_prompt}`",
            "",
            "**Exclude Styles:**",
            f"> `{self.suno.exclude_styles or 'None'}`",
            "",
            "**Lyrical Structure:**",
            "```text",
            self.suno.lyrics,
            "```",
            "",
            "---",
            "",
            "### 2. LYRIA 3.5 ENGINE OUTPUT (Narrative & Descriptive)",
            "**Descriptive Prompt:**",
            f"{self.lyria.narrative_prompt}",
            "",
            "**Structured Lyrics:**",
            "```text",
            self.lyria.lyrics,
            "```",
            "",
            "---",
            "",
            "### 3. COMPACT PARAMETER VECTOR & SECTION MAP",
            "**Section Map & Energy Arc:**",
            f"`{self.section_map}`",
            "",
            "**Compact Notation (§5):**",
            "```text",
            self.compact,
            "```",
        ]

        if self.assumptions:
            md_lines.extend([
                "",
                "**Assumptions Note:**",
                " · ".join(f"[{a}]" for a in self.assumptions),
            ])

        failed_checks = [c for c in self.checks if not c.passed]
        if failed_checks:
            md_lines.extend([
                "",
                "**Validation Warnings:**",
                *(f"- **{c.check_id}**: {c.message}" for c in failed_checks),
            ])

        return "\n".join(md_lines)
