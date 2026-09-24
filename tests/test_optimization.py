"""Unit tests for COMPOSER-160 Multi-Objective Optimization (Pareto Frontier)."""

import json
from pathlib import Path
import pytest

from composer160.cli import main
from composer160.core.vector import ParameterVector
from composer160.optimization.nsga2 import (
    DomainAwareCrossover,
    DomainAwareMutation,
    ParetoOptimizer,
    evolve,
    select_archetypes,
)
from composer160.optimization.objectives import (
    evaluate_objectives,
    f_identity,
    f_intent,
    f_novelty,
    f_validity,
)
from composer160.presets.aksan import aksan_preset
from composer160.repl import REPLSession


def test_objectives_scoring_bounds():
    """Verify all 4 objective functions return scores strictly within [0.0, 1.0]."""
    vec = aksan_preset()

    intent_score = f_intent(vec, "Melancholic dark alternative with duduk")
    identity_score = f_identity(vec)
    novelty_score = f_novelty(vec)
    validity_score = f_validity(vec)

    assert 0.0 <= intent_score <= 1.0
    assert 0.0 <= identity_score <= 1.0
    assert 0.0 <= novelty_score <= 1.0
    assert 0.0 <= validity_score <= 1.0

    # AKSAN preset should have high identity and flawless validity
    assert identity_score >= 0.90
    assert validity_score == 1.0


def test_intent_scoring_sensitivity():
    """Verify f_intent scores closer vectors higher than distant ones."""
    base = aksan_preset()

    target = base.copy()
    target.set(8, 120)
    target.set(100, "Anger")

    close_cand = base.copy()
    close_cand.set(8, 118)
    close_cand.set(100, "Anger")

    distant_cand = base.copy()
    distant_cand.set(8, 60)
    distant_cand.set(100, "Calm")

    assert f_intent(close_cand, target) > f_intent(distant_cand, target)


def test_validity_penalizes_incomplete_or_invalid_vectors():
    """Verify f_validity penalizes missing T1 fields or structural violations."""
    clean_vec = aksan_preset()
    assert f_validity(clean_vec) == 1.0

    broken_vec = clean_vec.copy()
    # Break C1 (remove T1 parameter 1 Root Key)
    broken_vec._values.pop(1, None)
    broken_score = f_validity(broken_vec)

    assert broken_score < 1.0


def test_domain_aware_crossover():
    """Verify crossover swaps complete domain groupings rather than fragmentary parameters."""
    parent_a = aksan_preset()
    parent_b = aksan_preset()

    # Distinguish parents on Domain B (Tempo & Meter: 8, 11, 15)
    parent_b.set(8, 130)
    parent_b.set(11, "7/8")
    parent_b.set(15, "Swing")

    crossover = DomainAwareCrossover(swap_probability=1.0)
    child_1, child_2 = crossover.cross(parent_a, parent_b)

    # In child_1, Domain B should match parent_b's complete set
    assert child_1.get(8) == 130
    assert child_1.get(11) == "7/8"
    assert child_1.get(15) == "Swing"

    # In child_2, Domain B should match parent_a's complete set
    assert child_2.get(8) == 86
    assert child_2.get(11) == "4/4"
    assert child_2.get(15) == "Straight"


def test_domain_aware_mutation():
    """Verify mutation perturbs values within legal registry boundaries."""
    mutator = DomainAwareMutation(mutation_rate=0.5)
    vec = aksan_preset()

    mutated = mutator.mutate(vec.copy())
    assert isinstance(mutated, ParameterVector)

    # BPM must remain within [60, 140]
    bpm = mutated.get(8)
    assert isinstance(bpm, int)
    assert 60 <= bpm <= 140


def test_nsga2_dominance_logic():
    """Verify Pareto dominance checks."""
    optimizer = ParetoOptimizer(population_size=10, generations=2)

    # A dominates B if strictly better in at least one and no worse in any
    a = (0.9, 0.9, 0.8, 1.0)
    b = (0.8, 0.9, 0.7, 1.0)
    assert optimizer._dominates(a, b) is True
    assert optimizer._dominates(b, a) is False

    # Trade-off solutions do not dominate each other
    c = (0.95, 0.70, 0.8, 1.0)
    assert optimizer._dominates(a, c) is False
    assert optimizer._dominates(c, a) is False


def test_nsga2_evolution_and_archetypes():
    """Verify evolve returns the 4 distinct non-dominated archetypes."""
    archetypes = evolve(
        user_request="Fast energetic rebellion with duduk and heavy electric guitar",
        population_size=10,
        generations=3,
        seed=42,
    )

    assert len(archetypes) == 5
    names = [arc.name for arc in archetypes]
    assert "The Purist" in names
    assert "The Electronic Neoclassical" in names
    assert "The Rebel" in names
    assert "The Avant-Garde" in names
    assert "The Knee-Point" in names

    for arc in archetypes:
        assert isinstance(arc.vector, ParameterVector)
        assert len(arc.suno_style) > 0
        assert len(arc.lyria_narrative) > 0
        assert len(arc.scores) == 4
        assert all(0.0 <= s <= 1.0 for s in arc.scores)


def test_repl_pareto_and_pick_commands(capsys):
    """Verify /pareto and /pick commands inside a REPL session."""
    session = REPLSession(use_llm=False)

    # 1. Run /pareto command
    assert session.handle_command("/pareto High energy dark rock") is True
    out = capsys.readouterr().out
    assert "PARETO FRONTIER ARCHETYPES" in out
    assert "THE PURIST" in out
    assert "THE REBEL" in out
    assert len(session.pareto_candidates) == 5

    # 2. Pick candidate 3 ("The Rebel")
    assert session.handle_command("/pick 3") is True
    out2 = capsys.readouterr().out
    assert "Selected [3] 'The Rebel' as active vector" in out2
    assert session.active_vector is not None


def test_cli_pareto_flag_json(capsys):
    """Verify CLI --pareto flag outputs valid JSON with 5 archetypes."""
    ret = main(["--pareto", "-p", "Fast dark rebellion", "-f", "json", "--no-llm"])
    assert ret == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "pareto_archetypes" in data
    assert len(data["pareto_archetypes"]) == 5

    names = [a["name"] for a in data["pareto_archetypes"]]
    assert "The Purist" in names
    assert "The Rebel" in names


def test_cli_pareto_flag_markdown(capsys):
    """Verify CLI --pareto flag outputs Markdown report."""
    ret = main(["--pareto", "-p", "Fast dark rebellion", "-f", "markdown", "--no-llm"])
    assert ret == 0

    captured = capsys.readouterr()
    assert "# COMPOSER-160 Multi-Objective Pareto Frontier Report" in captured.out
    assert "THE PURIST" in captured.out
    assert "THE REBEL" in captured.out
    assert "THE AVANT-GARDE" in captured.out
    assert "THE KNEE-POINT" in captured.out
