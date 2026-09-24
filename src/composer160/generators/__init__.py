"""COMPOSER-160 Generator Translators.

Contains specialized translators converting ParameterVector instances into
optimized prompts for Suno (tag-based) and Lyria 3.5 (narrative).
"""

from composer160.generators.base import GeneratorTranslator
from composer160.generators.lyria import LyriaOutput, LyriaTranslator
from composer160.generators.suno import SunoOutput, SunoTranslator

__all__ = [
    "GeneratorTranslator",
    "SunoOutput",
    "SunoTranslator",
    "LyriaOutput",
    "LyriaTranslator",
]
