"""Suno AI Music Generator Prompt Translator.

Translates a ParameterVector into Suno's dual-field architecture:
1. Style of Music: Front-loaded, comma-separated keywords (under character limits).
2. Exclude Styles: Clean comma-separated negative prompt suppressions.
3. Lyrics: Bracket-tagged arrangement script ([Verse], [Chorus], etc.).
"""

from dataclasses import dataclass
import re
from typing import Sequence

from composer160.core.vector import ParameterVector
from composer160.generators.base import GeneratorTranslator


@dataclass
class SunoOutput:
    """Structured output for the Suno AI music generator."""

    style_prompt: str
    exclude_styles: str | None
    lyrics: str


class SunoTranslator(GeneratorTranslator):
    """Converts a ParameterVector into Suno-compliant prompts."""

    def translate(
        self,
        vec: ParameterVector,
        lyrics: str | None = None,
        max_style_chars: int = 200,
    ) -> SunoOutput:
        """Translate a ParameterVector into SunoOutput.

        Args:
            vec: The input ParameterVector.
            lyrics: Optional lyrics text (raw stanzas or tagged).
            max_style_chars: Target character budget for the Style Prompt
                (defaults to 200; 120 for strict minimal mode).
        """
        style_prompt = self._build_style_prompt(vec, max_chars=max_style_chars)
        exclude_styles = self._build_exclude_styles(vec)
        formatted_lyrics = self._format_lyrics(vec, lyrics)

        return SunoOutput(
            style_prompt=style_prompt,
            exclude_styles=exclude_styles,
            lyrics=formatted_lyrics,
        )

    def _build_style_prompt(self, vec: ParameterVector, max_chars: int = 200) -> str:
        """Construct the front-loaded comma-separated style descriptor."""
        descriptors: list[str] = []

        # 1. Primary Genre & Core Aesthetic (highest weight in Suno)
        genres = vec.get(107)
        emotion = vec.get(100)
        brightness = vec.get(72)
        b_num = int(brightness) if (isinstance(brightness, (int, float)) or (isinstance(brightness, str) and brightness.isdigit())) else None
        genre_prefix = "dark" if (b_num is not None and b_num <= 2) else ""
        if isinstance(genres, (list, tuple)) and genres:
            primary_genre = f"{genre_prefix} {genres[0]}".strip().lower()
            descriptors.append(primary_genre)
            for g in genres[1:]:
                if g.lower() != "none" and len(descriptors) < 3:
                    descriptors.append(g.lower())
        elif isinstance(genres, str) and genres != "auto":
            descriptors.append(f"{genre_prefix} {genres}".strip().lower())

        if emotion != "auto" and emotion:
            descriptors.append(f"{str(emotion).lower()}")

        # 2. Vocal Identity (Gender & Delivery Style)
        vocal_presence = vec.get(117)
        if vocal_presence != "None (instrumental)" and vocal_presence != "auto":
            vocal_style = vec.get(119)
            vocal_type = vec.get(118)
            v_style_str = f"{vocal_style.lower()} " if (vocal_style != "auto" and vocal_style) else ""
            v_type_str = "male vocal" if (vocal_type in ("Tenor", "Baritone", "Bass")) else "vocal"
            descriptors.append(f"{v_style_str}{v_type_str}".strip())
        else:
            descriptors.append("instrumental")

        # 3. Signature Stems & Key Instruments
        stems = vec.get(144)
        if isinstance(stems, (list, tuple)) and stems:
            for inst in stems:
                inst_clean = str(inst).replace("lead vocal", "").strip()
                if inst_clean and inst_clean not in descriptors:
                    descriptors.append(inst_clean)
        else:
            inst_fam = vec.get(68)
            if isinstance(inst_fam, (list, tuple)):
                descriptors.extend(str(f).lower() for f in inst_fam[:3])

        # 4. Tempo, Key, and Meter
        bpm = vec.get(8)
        if bpm != "auto" and bpm:
            descriptors.append(f"{bpm} BPM")

        root_key = vec.get(1)
        tonality = vec.get(2)
        mode = vec.get(3)
        if root_key != "auto" and tonality != "auto":
            if tonality == "Minor":
                descriptors.append(f"{root_key} minor")
            elif tonality == "Modal" and mode != "auto":
                descriptors.append(f"{root_key} {mode}")
            elif tonality == "Major":
                descriptors.append(f"{root_key} major")

        # 5. Timbral Textures & Production Feel (Adjectives)
        warmth = vec.get(73)
        w_num = int(warmth) if (isinstance(warmth, (int, float)) or (isinstance(warmth, str) and warmth.isdigit())) else None
        if w_num is not None and w_num >= 4:
            descriptors.append("warm analog")

        depth = vec.get(108)
        if depth in ("Cathedral", "Cinematic", "Infinite"):
            descriptors.append("cinematic")

        # 6. Additional Nuances for Extended Character Budgets (up to 1000 chars)
        time_sig = vec.get(11)
        if time_sig != "auto" and time_sig:
            descriptors.append(f"{time_sig} time")
        groove = vec.get(15)
        if groove != "auto" and groove:
            descriptors.append(f"{str(groove).lower()} groove")

        prog_type = vec.get(45)
        if prog_type != "auto" and prog_type:
            descriptors.append(f"{str(prog_type).lower()} progression")
        chord_type = vec.get(40)
        if chord_type != "auto" and chord_type:
            descriptors.append(f"{str(chord_type).lower()} chords")

        bass_presence = vec.get(55)
        if bass_presence != "auto" and bass_presence:
            descriptors.append(f"{str(bass_presence).lower()} bassline")

        art = vec.get(77)
        if art != "auto" and art:
            descriptors.append(f"{str(art).lower()} articulation")
        dyn_shape = vec.get(81)
        if dyn_shape != "auto" and dyn_shape:
            descriptors.append(f"{str(dyn_shape).lower()}")

        rev_type = vec.get(111)
        if rev_type != "auto" and rev_type:
            descriptors.append(f"{str(rev_type).lower()} reverb")
        stereo = vec.get(109)
        if stereo != "auto" and stereo:
            descriptors.append(f"{str(stereo).lower()} stereo width")

        sat = vec.get(113)
        if sat != "auto" and sat:
            descriptors.append(f"{str(sat).lower()}")
        era = vec.get(140)
        if era != "auto" and era:
            descriptors.append(f"{str(era).lower()}")

        region = vec.get(141)
        if region != "auto" and region:
            descriptors.append(f"{str(region).lower()} traditional nuances")

        anchors = vec.get(139)
        if isinstance(anchors, (list, tuple)):
            for a in anchors:
                clean_anchor = re.sub(r"\s*[×x]\s*\d+(?:\.\d+)?", "", str(a)).strip()
                if clean_anchor and clean_anchor.lower() not in [d.lower() for d in descriptors]:
                    descriptors.append(clean_anchor.lower())

        # Assemble and respect character limit by dropping lowest priority terms
        style_str = ", ".join(descriptors)
        while len(style_str) > max_chars and len(descriptors) > 3:
            descriptors.pop()  # Drop tail descriptors
            style_str = ", ".join(descriptors)

        return style_str

    def _build_exclude_styles(self, vec: ParameterVector) -> str | None:
        """Assemble the Exclude Styles line from domains P (#135, #136) and S (#149)."""
        raw_items: list[str] = []

        for param_id in (149, 135, 136):
            val = vec.get(param_id)
            if val != "auto" and val is not None:
                if isinstance(val, (list, tuple, set)):
                    raw_items.extend(str(x) for x in val)
                elif isinstance(val, str):
                    raw_items.extend(val.split(","))

        if not raw_items:
            return None

        # Clean and deduplicate while preserving order
        seen: set[str] = set()
        cleaned_items: list[str] = []
        for item in raw_items:
            cleaned = item.strip().lower()
            if cleaned.startswith("no "):
                cleaned = cleaned[3:].strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                cleaned_items.append(cleaned)

        return ", ".join(cleaned_items) if cleaned_items else None

    def _format_lyrics(self, vec: ParameterVector, lyrics: str | None = None) -> str:
        """Format lyrics with Suno's bracketed meta-tags based on Section Map (#130)."""
        section_map = vec.get(130)

        # Extract section names from section_map
        section_names: list[str] = []
        if isinstance(section_map, (list, tuple)):
            for item in section_map:
                if isinstance(item, (list, tuple)) and item:
                    section_names.append(str(item[0]))
                elif isinstance(item, dict) and "name" in item:
                    section_names.append(str(item["name"]))
        elif isinstance(section_map, str):
            # Parse names from string format e.g. "Intro8 · V16 · Pre8 · Ch16"
            tokens = re.findall(r"([A-Za-z]+(?:\s*\d+)?)\d*", section_map)
            section_names = [t.strip() for t in tokens if t.strip()]

        if not section_names:
            section_names = ["Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Outro"]

        # Tag normalizer map
        def to_tag(name: str) -> str:
            lower = name.lower()
            if "intro" in lower:
                return "[Instrumental Intro]"
            if "pre" in lower:
                return "[Pre-Chorus]"
            if "chorus" in lower or "ch" in lower:
                num = re.findall(r"\d+", name)
                return f"[Chorus {num[0]}]" if num else "[Chorus]"
            if "verse" in lower or lower.startswith("v"):
                num = re.findall(r"\d+", name)
                return f"[Verse {num[0]}]" if num else "[Verse]"
            if "bridge" in lower or lower.startswith("br"):
                return "[Bridge]"
            if "solo" in lower:
                return "[Instrumental Solo]"
            if "outro" in lower:
                return "[Outro]"
            return f"[{name}]"

        tags = [to_tag(name) for name in section_names]

        # Case 1: Raw lyrics provided without brackets
        if lyrics:
            # Check if lyrics already has bracket tags
            if "[" in lyrics and "]" in lyrics:
                return lyrics.strip()

            # Split lyrics into stanzas by double newlines
            stanzas = [s.strip() for s in re.split(r"\n\s*\n", lyrics.strip()) if s.strip()]

            output_blocks: list[str] = []
            for i, tag in enumerate(tags):
                output_blocks.append(tag)
                if i < len(stanzas):
                    output_blocks.append(stanzas[i])
                output_blocks.append("")  # Blank line separator

            # If more stanzas than tags, append them at the end
            if len(stanzas) > len(tags):
                for stanza in stanzas[len(tags):]:
                    output_blocks.append(stanza)
                    output_blocks.append("")

            # Clean ending
            if "[Outro]" in tags and not any("[End]" in b for b in output_blocks):
                output_blocks.append("[Fade Out]")
                output_blocks.append("[End]")

            return "\n".join(output_blocks).strip()

        # Case 2: No lyrics provided — generate structural skeleton
        output_blocks = []
        for tag in tags:
            output_blocks.append(tag)
            output_blocks.append("")

        output_blocks.append("[Fade Out]")
        output_blocks.append("[End]")
        return "\n".join(output_blocks).strip()
