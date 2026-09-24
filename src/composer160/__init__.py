"""COMPOSER-160: Music Direction Engine (AKSAN Edition).

Translates musical intent into 160-parameter vectors and dual-format
prompts for Suno and Lyria 3.5 AI music generators.
"""

from composer160.core.parameters import (
    PARAMETER_REGISTRY,
    T1_PARAMETER_IDS,
    ParameterDef,
)
from composer160.core.types import Domain, ParamType, Tier
from composer160.core.vector import ParameterVector
from composer160.engine.interpreter import Interpreter
from composer160.generators.base import GeneratorTranslator
from composer160.generators.lyria import LyriaOutput, LyriaTranslator
from composer160.generators.suno import SunoOutput, SunoTranslator
from composer160.output.formatter import ComposerOutput
from composer160.output.notation import render_vector
from composer160.output.section_map import Section, SectionMapBuilder
from composer160.presets.aksan import aksan_preset
from composer160.repl import REPLSession, run_repl
from composer160.similarity.metric import distance
from composer160.validation.checks import CheckResult, Validator

__version__ = "0.1.0"


def compose(
    request_or_vec: str | ParameterVector | None = None,
    lyrics: str | None = None,
    max_suno_chars: int = 200,
    preset: str | ParameterVector = "aksan",
    use_llm: bool = True,
    llm_model: str = "gemini-2.5-flash",
) -> ComposerOutput:
    """Translate musical intent or a ParameterVector into dual-generator prompts.

    Args:
        request_or_vec: Natural language description of musical intent or an existing
            ParameterVector instance. If a string and use_llm=True, the request is
            interpreted by an LLM to derive parameter overrides.
        lyrics: Optional lyrics text (raw stanzas or tagged).
        max_suno_chars: Character limit for Suno style prompt (default 200).
        preset: Default preset name or vector to apply. Defaults to "aksan".
        use_llm: Whether to invoke the LLM interpreter when request_or_vec is a string.
        llm_model: Gemini model identifier (default: "gemini-2.5-flash").

    Returns:
        ComposerOutput with vector, compact notation, SunoOutput, LyriaOutput,
        section map, assumptions note, and validation results.
    """
    # 1. Resolve vector
    if isinstance(request_or_vec, ParameterVector):
        vec = request_or_vec
    elif isinstance(request_or_vec, str):
        base_vec = preset if isinstance(preset, ParameterVector) else aksan_preset()
        if use_llm:
            try:
                interpreter = Interpreter(model_name=llm_model, preset=base_vec)
                vec = interpreter.interpret_sync(request_or_vec)
            except Exception:
                # Graceful fallback to base preset if LLM call is unavailable
                vec = base_vec
        else:
            vec = base_vec
    elif isinstance(preset, ParameterVector):
        vec = preset
    else:
        vec = aksan_preset()

    # 2. Validate vector against C1–C7 rules
    validator = Validator()
    checks = validator.validate(vec)

    # 3. Build section map representation
    map_builder = SectionMapBuilder()
    sections = map_builder.build_from_vector(vec)
    map_str = map_builder.format_map(sections)
    energy_str = map_builder.format_energy(sections)
    section_map_display = f"{map_str} [{energy_str}]"

    # 4. Render compact vector notation
    compact_repr = render_vector(vec)

    # 5. Translate for Suno
    suno_translator = SunoTranslator()
    suno_out = suno_translator.translate(vec, lyrics=lyrics, max_style_chars=max_suno_chars)

    # 6. Translate for Lyria 3.5
    lyria_translator = LyriaTranslator()
    lyria_out = lyria_translator.translate(vec, lyrics=lyrics)

    # 7. Compile assumed T1 fields note
    assumed_fields = vec.assumed_t1_fields()
    assumptions_note = [f"{name}={val} [assumed]" for _, name, val in assumed_fields]

    return ComposerOutput(
        vector=vec,
        compact=compact_repr,
        suno=suno_out,
        lyria=lyria_out,
        section_map=section_map_display,
        assumptions=assumptions_note,
        checks=checks,
    )


__all__ = [
    "Domain",
    "ParamType",
    "Tier",
    "ParameterDef",
    "PARAMETER_REGISTRY",
    "T1_PARAMETER_IDS",
    "ParameterVector",
    "aksan_preset",
    "CheckResult",
    "Validator",
    "GeneratorTranslator",
    "SunoOutput",
    "SunoTranslator",
    "LyriaOutput",
    "LyriaTranslator",
    "Section",
    "SectionMapBuilder",
    "render_vector",
    "ComposerOutput",
    "Interpreter",
    "REPLSession",
    "run_repl",
    "distance",
    "compose",
]
