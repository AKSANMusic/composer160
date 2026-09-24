"""Google Lyria 3.5 AI Music Model Prompt Translator.

Translates a ParameterVector into Lyria 3.5's narrative architecture:
1. Narrative Prompt: Cohesive 3–5 sentence producer's brief (100–250 words)
   detailing genre, spatial instrument staging, vocal delivery, temporal arc,
   and mastering texture without brackets or comma-separated lists.
2. Structured Lyrics: Section-demarcated lyric arrangement for vocal synthesis.
"""

from dataclasses import dataclass
import re

from composer160.core.vector import ParameterVector
from composer160.generators.base import GeneratorTranslator


@dataclass
class LyriaOutput:
    """Structured output for Google's Lyria 3.5 generative music model."""

    narrative_prompt: str
    lyrics: str

    @property
    def word_count(self) -> int:
        """Return the word count of the narrative prompt."""
        return len(self.narrative_prompt.split())


class LyriaTranslator(GeneratorTranslator):
    """Converts a ParameterVector into Lyria 3.5-compliant narrative prompts."""

    def translate(self, vec: ParameterVector, lyrics: str | None = None) -> LyriaOutput:
        """Translate a ParameterVector into a LyriaOutput.

        Args:
            vec: The input ParameterVector.
            lyrics: Optional lyrics text to format.
        """
        narrative_prompt = self._build_narrative_prompt(vec)
        formatted_lyrics = self._format_lyrics(vec, lyrics)

        return LyriaOutput(
            narrative_prompt=narrative_prompt,
            lyrics=formatted_lyrics,
        )

    def _build_narrative_prompt(self, vec: ParameterVector) -> str:
        """Generate a 3–5 sentence cohesive producer's brief.

        Follows the 5-pillar structure:
        1. Genre, cultural lineage, and core emotional mood.
        2. Spatial instrument placement and stereo staging.
        3. Tempo, meter, groove, and vocal delivery style.
        4. Temporal progression and dynamic climax arc.
        5. Mastering texture, acoustic warmth, and anti-cliché production.
        """
        sentences: list[str] = []

        # =====================================================================
        # Sentence 1: Genre, Cultural Heritage, and Core Atmosphere
        # =====================================================================
        emotion = vec.get(100)
        genres = vec.get(107)
        regional = vec.get(141)

        emotion_map = {
            "melancholy": "melancholic",
            "nostalgia": "nostalgic",
            "tension": "tense",
            "serenity": "serene",
            "anger": "rebellious and defiant",
            "joy": "joyful",
            "sadness": "sorrowful",
            "fear": "haunting",
            "wonder": "wondrous",
            "triumph": "triumphant",
        }
        emotion_raw = str(emotion).lower() if (emotion != "auto" and emotion) else "melancholy"
        emotion_str = emotion_map.get(emotion_raw, emotion_raw)

        genre_parts: list[str] = []
        if isinstance(genres, (list, tuple)) and genres:
            genre_parts = [str(g).lower() for g in genres if str(g).lower() != "none"]
        elif isinstance(genres, str) and genres != "auto":
            genre_parts = [genres.lower()]

        primary_genre = " ".join(genre_parts[:2]) if genre_parts else "alternative"
        reg_note = ""
        if regional != "auto" and regional:
            reg_note = f", informed by {str(regional).lower()} melodic sensibilities"

        s1 = (
            f"A deeply {emotion_str} {primary_genre} piece rooted in cinematic minimalist brutalism"
            f"{reg_note} and dark emotional depth."
        )
        sentences.append(s1)

        # =====================================================================
        # Sentence 2: Spatial Instrumentation & Soundstage Placement
        # =====================================================================
        stems = vec.get(144)
        depth = vec.get(108)
        width = vec.get(109)

        depth_desc = "an intimate room ambience" if depth in ("Dry/close", "Room") else "a wide cinematic acoustic hall"
        width_desc = "across a broad stereo panorama" if width in ("Wide", "Ultra-wide") else "centered naturally in the soundstage"

        if isinstance(stems, (list, tuple)) and stems:
            inst_list = [str(s).lower() for s in stems if "vocal" not in str(s).lower()]
            if len(inst_list) >= 3:
                lead_inst = inst_list[0]
                inst_text = f"{lead_inst}, {inst_list[1]}, and {inst_list[2]}"
                s2 = (
                    f"An intimate acoustic upright bass grounds the low end with warm woody resonance, "
                    f"while expressive {inst_text} float {width_desc} with {depth_desc}."
                )
            elif len(inst_list) == 2:
                s2 = (
                    f"An intimate acoustic upright bass grounds the low end with warm woody resonance, "
                    f"while expressive {inst_list[0]} and {inst_list[1]} float {width_desc} with {depth_desc}."
                )
            elif len(inst_list) == 1:
                s2 = (
                    f"An intimate acoustic upright bass grounds the low end with warm woody resonance, "
                    f"while expressive {inst_list[0]} floats {width_desc} with {depth_desc}."
                )
            else:
                s2 = f"Acoustic instruments and warm textures occupy distinct spatial layers {width_desc} with {depth_desc}."
        else:
            s2 = f"Acoustic instrumentation and understated rhythmic textures are staged {width_desc} within {depth_desc}."
        sentences.append(s2)

        # =====================================================================
        # Sentence 3: Tempo, Meter, Groove, and Vocal Performance
        # =====================================================================
        bpm = vec.get(8)
        time_sig = vec.get(11)
        groove = vec.get(15)
        vocal_presence = vec.get(117)
        vocal_style = vec.get(119)
        vocal_type = vec.get(118)
        percussion = vec.get(20)

        bpm_str = f"{bpm} BPM" if (bpm != "auto" and bpm) else "moderate tempo"
        time_str = f" in {time_sig} time" if (time_sig != "auto" and time_sig) else ""
        groove_str = f"a {str(groove).lower()} groove" if (groove != "auto" and groove) else "steady momentum"

        perc_str = "soft brush drums and subtle percussion" if percussion in ("Minimal", "Standard") else "restrained percussion"

        if vocal_presence != "None (instrumental)" and vocal_presence != "auto":
            v_style = str(vocal_style).lower() if (vocal_style != "auto" and vocal_style) else "emotionally raw"
            v_gender = "male" if vocal_type in ("Tenor", "Baritone", "Bass") else "lead"
            vocal_phrase = f"a {v_style} {v_gender} vocal delivering lyrics with natural, speech-like phrasing"
        else:
            vocal_phrase = "an evocative melodic lead carrying the contemplative theme without sung vocals"

        s3 = f"Driven by {perc_str} at {bpm_str}{time_str} with {groove_str}, the performance centers around {vocal_phrase}."
        sentences.append(s3)

        # =====================================================================
        # Sentence 4: Temporal Progression and Dynamic Arc
        # =====================================================================
        intro = vec.get(92)
        buildup = vec.get(94)
        climax = vec.get(95)
        ending = vec.get(99)

        intro_desc = "a quiet ambient introduction" if intro in ("Ambient", "Melodic") else "a spare rhythmic opening"
        build_desc = "gradually swells through layered acoustic textures" if buildup in ("Gradual layers", "Rhythmic intensification") else "builds steadily"
        climax_desc = "a poignant, heart-wrenching emotional peak" if (isinstance(climax, (int, float)) and climax >= 4) else "a focused dynamic peak"
        ending_desc = "a lingering acoustic fade-out" if ending in ("Fade-out", "Ritardando") else "a resolute final cadence"

        s4 = (
            f"The progression commences with {intro_desc}, {build_desc} toward {climax_desc}, "
            f"and gently resolves into {ending_desc}."
        )
        sentences.append(s4)

        # =====================================================================
        # Sentence 5: Production Aesthetic, Mastering Texture & Tape Grain
        # =====================================================================
        warmth = vec.get(73)
        saturation = vec.get(113)

        tape_grain = "subtle 16mm film grain analogue tape warmth" if saturation in ("Subtle warmth", "Grit") or (warmth != "auto" and warmth >= 4) else "warm analog tape character"

        s5 = (
            f"The final master embraces {tape_grain}, transparent acoustic headroom, and natural room decay, "
            f"deliberately avoiding over-compression, electronic risers, or aggressive modern pop gloss."
        )
        sentences.append(s5)

        return " ".join(sentences)

    def _format_lyrics(self, vec: ParameterVector, lyrics: str | None = None) -> str:
        """Format lyrics with structural section markers compatible with Lyria."""
        section_map = vec.get(130)

        # Extract section names
        section_names: list[str] = []
        if isinstance(section_map, (list, tuple)):
            for item in section_map:
                if isinstance(item, (list, tuple)) and item:
                    section_names.append(str(item[0]))
                elif isinstance(item, dict) and "name" in item:
                    section_names.append(str(item["name"]))

        if not section_names:
            section_names = ["Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Bridge", "Outro"]

        if lyrics:
            # If lyrics already contain bracket tags, clean and format
            if "[" in lyrics and "]" in lyrics:
                return lyrics.strip()

            stanzas = [s.strip() for s in re.split(r"\n\s*\n", lyrics.strip()) if s.strip()]
            blocks: list[str] = []

            for i, name in enumerate(section_names):
                blocks.append(f"[{name}]")
                if i < len(stanzas):
                    blocks.append(stanzas[i])
                blocks.append("")

            if len(stanzas) > len(section_names):
                for stanza in stanzas[len(section_names):]:
                    blocks.append(stanza)
                    blocks.append("")

            return "\n".join(blocks).strip()

        # Skeleton markers
        blocks = []
        for name in section_names:
            blocks.append(f"[{name}]")
            blocks.append("")
        return "\n".join(blocks).strip()
