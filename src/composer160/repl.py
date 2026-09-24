"""Interactive REPL Mode for COMPOSER-160.

Allows continuous, iterative natural language refinement of musical parameters,
displaying diffs after each prompt, and supporting session persistence via .c160 files.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

from composer160.core.parameters import PARAMETER_REGISTRY
from composer160.core.vector import ParameterVector
from composer160.engine.interpreter import Interpreter
from composer160.generators.lyria import LyriaTranslator
from composer160.generators.suno import SunoTranslator
from composer160.output.notation import render_vector
from composer160.output.section_map import SectionMapBuilder
from composer160.presets.aksan import aksan_preset
from composer160.validation.checks import Validator


def compute_vector_diff(
    vec_a: ParameterVector, vec_b: ParameterVector
) -> dict[int, tuple[Any, Any]]:
    """Compute differences between two parameter vectors.

    Returns a dict mapping param_id -> (val_a, val_b).
    """
    diffs: dict[int, tuple[Any, Any]] = {}
    for pid in range(1, 161):
        val_a = vec_a.get(pid)
        val_b = vec_b.get(pid)
        if val_a != val_b:
            diffs[pid] = (val_a, val_b)
    return diffs


def format_vector_diff(diffs: dict[int, tuple[Any, Any]]) -> str:
    """Format parameter differences into a concise human-readable string."""
    if not diffs:
        return "No parameter changes detected."

    lines: list[str] = [f"Changes applied ({len(diffs)} parameter{'s' if len(diffs) != 1 else ''} modified):"]
    for pid, (old_v, new_v) in sorted(diffs.items()):
        defn = PARAMETER_REGISTRY.get(pid)
        name = defn.name if defn else f"Param {pid}"
        tier = f"[{defn.tier.name}]" if defn else ""
        lines.append(f"  • #{pid:3d} {name} {tier}: {old_v!r} ➔ {new_v!r}")
    return "\n".join(lines)


class REPLSession:
    """Manages an interactive COMPOSER-160 music direction session."""

    def __init__(
        self,
        initial_vector: ParameterVector | None = None,
        load_file: str | Path | None = None,
        lyrics: str | None = None,
        model: str = "gemini-2.5-flash",
        use_llm: bool = True,
    ) -> None:
        self.model = model
        self.use_llm = use_llm
        self.lyrics = lyrics

        if load_file is not None:
            self.active_vector = ParameterVector.load_from_file(load_file)
            self.loaded_from: str | None = str(load_file)
        elif initial_vector is not None:
            self.active_vector = initial_vector.copy()
            self.loaded_from = None
        else:
            self.active_vector = aksan_preset()
            self.loaded_from = None

        self.initial_vector = self.active_vector.copy()
        self.history: list[tuple[str, dict[int, tuple[Any, Any]]]] = []

        self.interpreter = Interpreter(model_name=self.model, preset=self.active_vector)
        self.validator = Validator()
        self.suno_translator = SunoTranslator()
        self.lyria_translator = LyriaTranslator()
        self.map_builder = SectionMapBuilder()
        self.pareto_candidates: list[Any] = []

    def handle_command(self, cmd_line: str) -> bool:
        """Handle a slash command. Returns False if REPL should exit, True to continue."""
        parts = cmd_line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("/exit", "/quit", "/q"):
            print("Exiting COMPOSER-160 session. Goodbye!")
            return False

        if cmd == "/save":
            self._handle_save(args)
        elif cmd == "/load":
            self._handle_load(args)
        elif cmd in ("/show", "/output"):
            self._handle_show(args)
        elif cmd == "/diff":
            self._handle_diff()
        elif cmd == "/compact":
            self._handle_compact()
        elif cmd in ("/validate", "/checks"):
            self._handle_validate()
        elif cmd == "/pareto":
            self._handle_pareto(args)
        elif cmd == "/pick":
            self._handle_pick(args)
        elif cmd == "/lyrics":
            self._handle_lyrics(args)
        elif cmd == "/reset":
            self._handle_reset()
        elif cmd in ("/help", "/h", "/?"):
            self._handle_help()
        else:
            print(f"Unknown command: '{cmd}'. Type /help for available commands.")

        return True

    def _handle_save(self, filepath: str) -> None:
        target = filepath or "session.c160"
        if not target.endswith(".c160"):
            target += ".c160"
        try:
            self.active_vector.save_to_file(target)
            print(f"✓ Saved active vector ({len(self.active_vector)} parameters) to '{target}'")
        except Exception as e:
            print(f"✗ Failed to save to '{target}': {e}")

    def _handle_load(self, filepath: str) -> None:
        if not filepath:
            print("Usage: /load <filename>.c160")
            return
        target = filepath
        if not target.endswith(".c160") and not Path(target).exists():
            target += ".c160"
        try:
            loaded_vec = ParameterVector.load_from_file(target)
            self.active_vector = loaded_vec
            self.loaded_from = target
            print(f"✓ Successfully loaded vector from '{target}'")
            checks = self.validator.validate(self.active_vector)
            failed = [c for c in checks if not c.passed]
            if failed:
                print(f"  Warning: {len(failed)} validation checks failed in loaded vector.")
        except Exception as e:
            print(f"✗ Failed to load '{target}': {e}")

    def _handle_show(self, args: str = "") -> None:
        """Render and print Suno, Lyria 3.5, and structure details."""
        suno_out = self.suno_translator.translate(self.active_vector, lyrics=self.lyrics)
        lyria_out = self.lyria_translator.translate(self.active_vector, lyrics=self.lyrics)
        sections = self.map_builder.build_from_vector(self.active_vector)
        map_str = self.map_builder.format_map(sections)
        energy_str = self.map_builder.format_energy(sections)

        print("\n" + "=" * 65)
        print(" COMPOSER-160 CURRENT GENERATION PREVIEW")
        print("=" * 65)
        print(f"Section Map: {map_str} [{energy_str}]")
        print("-" * 65)
        print(f"SUNO STYLE PROMPT ({len(suno_out.style_prompt)} chars):")
        print(f"  {suno_out.style_prompt}")
        if suno_out.exclude_styles:
            print(f"SUNO EXCLUDE STYLES:")
            print(f"  {suno_out.exclude_styles}")
        if self.lyrics:
            print(f"SUNO BRACKETED LYRICS:")
            for line in suno_out.lyrics.splitlines()[:10]:
                print(f"  {line}")
            if len(suno_out.lyrics.splitlines()) > 10:
                print("  ...")
        print("-" * 65)
        print(f"GOOGLE LYRIA 3.5 NARRATIVE ({lyria_out.word_count} words):")
        print(f"  {lyria_out.narrative_prompt}")
        print("=" * 65 + "\n")

    def _handle_diff(self) -> None:
        """Show diff between current state and session initial state."""
        diffs = compute_vector_diff(self.initial_vector, self.active_vector)
        print("\nSession Diff (vs Initial State):")
        print(format_vector_diff(diffs))
        print()

    def _handle_compact(self) -> None:
        print("\nCompact Bracket Notation (§5):")
        print(render_vector(self.active_vector))
        print()

    def _handle_validate(self) -> None:
        checks = self.validator.validate(self.active_vector)
        print("\nC1–C7 Validation Results:")
        for c in checks:
            status = "✓ PASS" if c.passed else "✗ FAIL"
            fix = f" [AUTO-FIX: {c.fix_description}]" if c.auto_fixed else ""
            print(f"  {status}: {c.check_id} - {c.message}{fix}")
        print()

    def _handle_lyrics(self, args: str) -> None:
        if not args:
            if self.lyrics:
                print("\nCurrent Lyrics:")
                print(self.lyrics)
            else:
                print("No lyrics currently set. Use `/lyrics <text>` or `/lyrics <file.txt>` to set.")
            return

        if os.path.isfile(args):
            try:
                with open(args, "r", encoding="utf-8") as f:
                    self.lyrics = f.read().strip()
                print(f"✓ Loaded lyrics from '{args}'")
            except Exception as e:
                print(f"✗ Failed to read lyrics file '{args}': {e}")
        else:
            self.lyrics = args.strip()
            print(f"✓ Updated lyrics ({len(self.lyrics.splitlines())} lines)")

    def _handle_reset(self) -> None:
        self.active_vector = self.initial_vector.copy()
        print("✓ Reset active vector back to initial session state.")

    def _handle_pareto(self, prompt: str) -> None:
        """Run NSGA-II multi-objective optimizer and display 4 Pareto archetypes."""
        from composer160.optimization.nsga2 import evolve

        request = prompt.strip() or "Melankolik Asi alternative rock"
        print(f"\nEvolving Pareto Frontier for intent: '{request}' (NSGA-II)...")
        try:
            self.pareto_candidates = evolve(
                user_request=request,
                base_preset=self.active_vector,
                lyrics=self.lyrics,
                population_size=20,
                generations=10,
            )
        except Exception as e:
            print(f"✗ Pareto optimization failed: {e}")
            return

        print("\n" + "=" * 78)
        print("  PARETO FRONTIER ARCHETYPES (Non-dominated Multi-Objective Candidates)")
        print("=" * 78)
        for i, arc in enumerate(self.pareto_candidates, start=1):
            print(f"[{i}] {arc.name.upper()} ({arc.archetype_id})")
            print(f"    • Focus:    {arc.description}")
            print(
                f"    • Scores:   Intent: {arc.intent_score:.2f} | "
                f"Identity: {arc.identity_score:.2f} | "
                f"Novelty: {arc.novelty_score:.2f} | "
                f"Validity: {arc.validity_score:.2f}"
            )
            print(f"    • Style:    {arc.suno_style[:90]}...")
            print(f"    • Map:      {arc.section_map}")
            print("-" * 78)
        print("Type `/pick <1-4>` to set any archetype as your active vector, or `/show` to inspect.")
        print("=" * 78 + "\n")

    def _handle_pick(self, selection: str) -> None:
        """Select one of the 4 Pareto archetypes as the active vector."""
        if not self.pareto_candidates:
            print("No Pareto candidates available. Run `/pareto <prompt>` first.")
            return

        try:
            choice = int(selection.strip())
            if not (1 <= choice <= len(self.pareto_candidates)):
                raise ValueError
        except ValueError:
            print(f"Please specify a number between 1 and {len(self.pareto_candidates)} (e.g. `/pick 2`).")
            return

        chosen = self.pareto_candidates[choice - 1]
        old_vec = self.active_vector
        self.active_vector = chosen.vector.copy()
        diffs = compute_vector_diff(old_vec, self.active_vector)
        self.history.append((f"Picked Pareto [{choice}] {chosen.name}", diffs))

        print(f"✓ Selected [{choice}] '{chosen.name}' as active vector!")
        print(f"  Focus: {chosen.description}")
        print(f"  Section Map: {chosen.section_map}")
        print("  Type `/show` to view the complete Suno & Lyria prompts for this archetype.")

    def _handle_help(self) -> None:
        print(
            "\nCOMPOSER-160 REPL Commands:\n"
            "  /show               Display Suno and Lyria 3.5 generation outputs\n"
            "  /diff               Show all modified parameters since session start\n"
            "  /save [file.c160]   Save current vector to a .c160 JSON file\n"
            "  /load <file.c160>   Load a vector from a .c160 JSON file\n"
            "  /compact            Print compact bracket notation (§5)\n"
            "  /validate           Run C1–C7 mathematical validation checks\n"
            "  /pareto [prompt]    Run NSGA-II multi-objective optimizer and view 4 Pareto archetypes\n"
            "  /pick <1-4>         Select one of the 4 Pareto archetypes as active vector\n"
            "  /lyrics [text|file] View or update session lyrics\n"
            "  /reset              Reset active vector to session start\n"
            "  /help               Show this help message\n"
            "  /exit, /quit, /q    Exit the interactive session\n"
            "\nNatural Language Tweaks:\n"
            "  Type any musical instruction to iteratively adjust parameters.\n"
            "  Examples:\n"
            "    • 'Increase tempo to 98 BPM and add electric guitar solo in bridge'\n"
            "    • 'Change tonality to D minor and make vocal style breathy tenor'\n"
            "    • 'Make the mood darker and add duduk lead'\n"
        )

    def apply_tweak(self, user_prompt: str) -> dict[int, tuple[Any, Any]]:
        """Apply a natural language tweak via the LLM and return the diff."""
        if not self.use_llm:
            print("Notice: LLM interpretation is disabled (--no-llm).")
            return {}

        try:
            new_vector = self.interpreter.interpret_sync(
                user_prompt, base_vector=self.active_vector
            )
        except Exception as e:
            print(f"✗ Interpretation failed: {e}")
            return {}

        diffs = compute_vector_diff(self.active_vector, new_vector)
        if diffs:
            self.active_vector = new_vector
            self.history.append((user_prompt, diffs))

        return diffs


def run_repl(
    initial_vector: ParameterVector | None = None,
    load_file: str | Path | None = None,
    lyrics: str | None = None,
    model: str = "gemini-2.5-flash",
    use_llm: bool = True,
) -> None:
    """Start an interactive COMPOSER-160 session in the terminal."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    try:
        session = REPLSession(
            initial_vector=initial_vector,
            load_file=load_file,
            lyrics=lyrics,
            model=model,
            use_llm=use_llm,
        )
    except Exception as e:
        print(f"Error initializing session: {e}", file=sys.stderr)
        return

    print("=" * 65)
    print("  COMPOSER-160 Interactive Session (AKSAN Edition)")
    print("=" * 65)
    if session.loaded_from:
        print(f"Loaded vector: {session.loaded_from}")
    else:
        print("Base preset: AKSAN 'Melankolik Asi' (75 bars @ 86 BPM)")
    print("Type your musical tweaks in natural language, or /help for commands.")
    print("Type /show to preview Suno & Lyria prompts, /exit to quit.\n")

    while True:
        try:
            user_input = input("composer160> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting COMPOSER-160 session. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            should_continue = session.handle_command(user_input)
            if not should_continue:
                break
        else:
            diffs = session.apply_tweak(user_input)
            print(format_vector_diff(diffs))
            print()
