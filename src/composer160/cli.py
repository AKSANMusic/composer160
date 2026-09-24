"""COMPOSER-160 Command Line Interface.

Provides a terminal interface for generating Suno and Lyria 3.5 prompts
from natural language descriptions or presets.
"""

import argparse
import os
import sys
from typing import Sequence

from composer160 import compose


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for COMPOSER-160 music direction."""
    # Ensure stdout/stderr handle UTF-8 properly across operating systems
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="composer160",
        description="COMPOSER-160: Music Direction Engine (AKSAN Edition) for Suno & Lyria 3.5",
    )
    parser.add_argument(
        "positional_prompt",
        nargs="?",
        default=None,
        help="Musical request description or intent (e.g. 'Dark Anatolian alternative with duduk')",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        dest="flag_prompt",
        default=None,
        help="Musical request description (alternative to positional argument)",
    )
    parser.add_argument(
        "--lyrics",
        "-l",
        default=None,
        help="Lyrics string or path to a text file containing lyrics",
    )
    parser.add_argument(
        "--preset",
        default="aksan",
        help="Base preset name (default: 'aksan')",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format: markdown (default) or json",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM interpretation and rely purely on preset defaults",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model identifier for intent interpretation (default: 'gemini-2.5-flash')",
    )
    parser.add_argument(
        "--max-suno-chars",
        type=int,
        default=200,
        help="Character limit for the Suno style prompt (default: 200)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Launch interactive REPL mode for iterative prompt refinement",
    )
    parser.add_argument(
        "--load",
        default=None,
        help="Load a saved .c160 parameter vector file",
    )
    parser.add_argument(
        "--pareto",
        action="store_true",
        help="Run NSGA-II multi-objective optimizer and output 4 diverse Pareto archetypes",
    )

    args = parser.parse_args(argv)

    # Resolve prompt
    prompt = args.flag_prompt or args.positional_prompt

    # Resolve lyrics (check if path to file)
    lyrics = args.lyrics
    if lyrics and os.path.isfile(lyrics):
        try:
            with open(lyrics, "r", encoding="utf-8") as f:
                lyrics = f.read()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to read lyrics file '{args.lyrics}': {e}\n")

    # Check for interactive REPL mode
    if args.interactive:
        from composer160.repl import run_repl

        run_repl(
            load_file=args.load,
            lyrics=lyrics,
            model=args.model,
            use_llm=not args.no_llm,
        )
        return 0

    # Load vector file if provided in batch/single-shot mode
    base_preset = args.preset
    if args.load:
        from composer160.core.vector import ParameterVector

        try:
            base_preset = ParameterVector.load_from_file(args.load)
        except Exception as e:
            sys.stderr.write(f"Error loading vector from '{args.load}': {e}\n")
            return 1

    # Check for Pareto multi-objective optimization mode
    if args.pareto:
        import json
        from composer160.core.vector import ParameterVector
        from composer160.optimization.nsga2 import evolve
        from composer160.presets.aksan import aksan_preset

        prompt_str = prompt or "Melankolik Asi alternative rock"
        base = base_preset if isinstance(base_preset, ParameterVector) else aksan_preset()
        archetypes = evolve(
            user_request=prompt_str,
            base_preset=base,
            lyrics=lyrics,
            population_size=20,
            generations=10,
        )

        if args.format == "json":
            data = {
                "pareto_archetypes": [
                    {
                        "index": i + 1,
                        "name": arc.name,
                        "id": arc.archetype_id,
                        "description": arc.description,
                        "scores": {
                            "intent": round(arc.intent_score, 2),
                            "identity": round(arc.identity_score, 2),
                            "novelty": round(arc.novelty_score, 2),
                            "validity": round(arc.validity_score, 2),
                        },
                        "suno_style": arc.suno_style,
                        "lyria_narrative": arc.lyria_narrative,
                        "section_map": arc.section_map,
                        "compact_vector": arc.vector.to_compact(),
                    }
                    for i, arc in enumerate(archetypes)
                ]
            }
            sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        else:
            lines = [
                "# COMPOSER-160 Multi-Objective Pareto Frontier Report",
                "",
                "Evolved 4 diverse, non-dominated archetypes balancing Intent, Identity, Novelty, and Validity:",
                "",
            ]
            for i, arc in enumerate(archetypes, start=1):
                lines.append(f"## [{i}] {arc.name.upper()} (`{arc.archetype_id}`)")
                lines.append(f"> **Focus:** {arc.description}")
                lines.append("")
                lines.append(
                    f"**Fitness Scores:** Intent: `{arc.intent_score:.2f}` | "
                    f"Identity: `{arc.identity_score:.2f}` | "
                    f"Novelty: `{arc.novelty_score:.2f}` | "
                    f"Validity: `{arc.validity_score:.2f}`"
                )
                lines.append(f"- **Section Map:** `{arc.section_map}`")
                lines.append(f"- **Suno Style Prompt:** `{arc.suno_style}`")
                lines.append(f"- **Lyria Narrative:** {arc.lyria_narrative}")
                lines.append("")
                lines.append("```text")
                lines.append(arc.vector.to_compact())
                lines.append("```")
                lines.append("---")
                lines.append("")
            sys.stdout.write("\n".join(lines) + "\n")

        return 0

    # Run standard compose pipeline
    try:
        output = compose(
            request_or_vec=prompt,
            lyrics=lyrics,
            max_suno_chars=args.max_suno_chars,
            preset=base_preset,
            use_llm=not args.no_llm,
            llm_model=args.model,
        )

        if args.format == "json":
            sys.stdout.write(output.to_json() + "\n")
        else:
            sys.stdout.write(output.to_markdown() + "\n")

        return 0
    except Exception as e:
        sys.stderr.write(f"Error during COMPOSER-160 execution: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
