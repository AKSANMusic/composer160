"""COMPOSER-160 Output Formatting Module.

Contains Section Map modeling, compact bracket vector notation rendering,
and the ComposerOutput dataclass.
"""

from composer160.output.formatter import ComposerOutput
from composer160.output.notation import render_vector
from composer160.output.section_map import Section, SectionMapBuilder

__all__ = [
    "Section",
    "SectionMapBuilder",
    "render_vector",
    "ComposerOutput",
]
