"""Dependency-free NSGA-II Multi-Objective Optimizer for COMPOSER-160.

Evolves populations of 160-parameter vectors to find the Pareto Frontier
balancing user intent, aesthetic identity, novelty, and harmonic validity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any, Sequence

from composer160.core.parameters import PARAMETER_REGISTRY
from composer160.core.types import Domain
from composer160.core.vector import ParameterVector
from composer160.generators.lyria import LyriaTranslator
from composer160.generators.suno import SunoTranslator
from composer160.optimization.objectives import evaluate_objectives
from composer160.output.section_map import SectionMapBuilder
from composer160.presets.aksan import aksan_preset
from composer160.validation.checks import Validator


@dataclass
class ParetoArchetype:
    """A representative solution selected from the Pareto Frontier."""

    name: str
    archetype_id: str
    description: str
    vector: ParameterVector
    scores: tuple[float, float, float, float]  # (intent, identity, novelty, validity)
    suno_style: str
    lyria_narrative: str
    section_map: str

    @property
    def intent_score(self) -> float:
        return self.scores[0]

    @property
    def identity_score(self) -> float:
        return self.scores[1]

    @property
    def novelty_score(self) -> float:
        return self.scores[2]

    @property
    def validity_score(self) -> float:
        return self.scores[3]


class DomainAwareCrossover:
    """Swaps parameter subsets grouped by their Domain (A–T) between parents."""

    def __init__(self, swap_probability: float = 0.5) -> None:
        self.swap_probability = swap_probability

    def cross(
        self, parent_a: ParameterVector, parent_b: ParameterVector
    ) -> tuple[ParameterVector, ParameterVector]:
        """Produce two offspring by domain-level crossover."""
        child_1 = parent_a.copy()
        child_2 = parent_b.copy()

        # Group parameter IDs by domain
        domain_params: dict[Domain, list[int]] = {}
        for pid, defn in PARAMETER_REGISTRY.items():
            domain_params.setdefault(defn.domain, []).append(pid)

        for domain, pids in domain_params.items():
            if random.random() < self.swap_probability:
                for pid in pids:
                    # Swap parameters for this entire domain
                    val_a = child_1.get(pid)
                    val_b = child_2.get(pid)
                    child_1.set(pid, val_b)
                    child_2.set(pid, val_a)

        return child_1, child_2


class DomainAwareMutation:
    """Mutates parameter values within legal domain boundaries."""

    def __init__(self, mutation_rate: float = 0.12) -> None:
        self.mutation_rate = mutation_rate

    def mutate(self, vec: ParameterVector) -> ParameterVector:
        """Mutate a parameter vector in-place and return it."""
        for pid in range(1, 161):
            if random.random() > self.mutation_rate:
                continue

            defn = PARAMETER_REGISTRY.get(pid)
            if defn is None:
                continue

            # 1. Mutate numeric BPM (#8)
            if pid == 8:
                curr_bpm = int(vec.get(8)) if vec.is_set(8) else 86
                delta = random.choice([-6, -4, -2, 2, 4, 6])
                new_bpm = max(60, min(140, curr_bpm + delta))
                vec.set(8, new_bpm)

            # 2. Mutate discrete rating scale [1–5] as integers
            elif pid in (5, 16, 17, 19, 24, 35, 47, 50, 61, 72, 73, 86, 91, 95, 103, 110, 116, 126, 128, 137, 143):
                curr = vec.get(pid)
                curr_val = int(curr) if (vec.is_set(pid) and str(curr).isdigit()) else 3
                new_val = max(1, min(5, curr_val + random.choice([-1, 1])))
                vec.set(pid, new_val)

            # 3. Mutate Mode (#3)
            elif pid == 3:
                vec.set(3, random.choice(["Aeolian", "Dorian", "Phrygian", "Harmonic minor", "Melodic minor"]))

            # 4. Mutate Meter (#11)
            elif pid == 11:
                vec.set(11, random.choice(["4/4", "7/8", "6/8", "3/4"]))

            # 5. Mutate Emotion (#100)
            elif pid == 100:
                vec.set(100, random.choice(["Melancholy", "Grief", "Longing", "Tension", "Defiance"]))

            # 6. Fallback generic categorical choices
            elif defn.values and len(defn.values) > 1:
                current = vec.get(pid)
                choices = [v for v in defn.values if v != current]
                if choices:
                    chosen = random.choice(choices)
                    vec.set(pid, int(chosen) if (str(chosen).isdigit() and len(str(chosen)) == 1) else chosen)

        return vec


class ParetoOptimizer:
    """Non-dominated Sorting Genetic Algorithm (NSGA-II) for COMPOSER-160."""

    def __init__(
        self,
        population_size: int = 20,
        generations: int = 10,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.12,
        seed: int | None = None,
    ) -> None:
        self.pop_size = max(8, population_size)
        self.generations = max(2, generations)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.validator = Validator()
        self.crossover = DomainAwareCrossover()
        self.mutator = DomainAwareMutation(mutation_rate=self.mutation_rate)

        if seed is not None:
            random.seed(seed)

    def _init_population(
        self, target_vec: ParameterVector, base_preset: ParameterVector
    ) -> list[ParameterVector]:
        """Initialize diverse population seeding from base preset and target vector."""
        population: list[ParameterVector] = [
            base_preset.copy(),
            target_vec.copy(),
        ]

        # Seed variations with specific musical biases
        # Rebel / High Energy seed
        rebel_seed = target_vec.copy()
        rebel_seed.set(8, min(120, (target_vec.get(8) if target_vec.is_set(8) else 86) + 12))
        rebel_seed.set(103, 5)  # Peak tension
        rebel_seed.set(95, 5)   # Peak climax
        rebel_seed.set(80, "Wide")
        rebel_seed.set(119, "Belting")
        population.append(rebel_seed)

        # Avant-Garde / Novelty seed
        avant_seed = target_vec.copy()
        avant_seed.set(3, "Phrygian")
        avant_seed.set(11, "7/8")
        avant_seed.set(40, "9ths")
        avant_seed.set(50, 4)   # Higher dissonance
        avant_seed.set(108, "Infinite")
        population.append(avant_seed)

        # Fill remainder with mutated recombinations
        while len(population) < self.pop_size:
            parent = random.choice([base_preset, target_vec, rebel_seed, avant_seed])
            clone = parent.copy()
            mutated = self.mutator.mutate(clone)
            population.append(mutated)

        return population[: self.pop_size]

    def _dominates(self, a_scores: Sequence[float], b_scores: Sequence[float]) -> bool:
        """Return True if score vector A Pareto-dominates score vector B (maximization)."""
        not_worse = all(a >= b for a, b in zip(a_scores, b_scores))
        strictly_better = any(a > b for a, b in zip(a_scores, b_scores))
        return not_worse and strictly_better

    def _fast_non_dominated_sort(
        self, pop_scores: list[tuple[float, float, float, float]]
    ) -> list[list[int]]:
        """Sort population indices into Pareto fronts."""
        n = len(pop_scores)
        domination_counts = [0] * n
        dominated_indices: list[list[int]] = [[] for _ in range(n)]
        fronts: list[list[int]] = [[]]

        for p in range(n):
            for q in range(n):
                if p == q:
                    continue
                if self._dominates(pop_scores[p], pop_scores[q]):
                    dominated_indices[p].append(q)
                elif self._dominates(pop_scores[q], pop_scores[p]):
                    domination_counts[p] += 1

            if domination_counts[p] == 0:
                fronts[0].append(p)

        i = 0
        while len(fronts[i]) > 0:
            next_front: list[int] = []
            for p in fronts[i]:
                for q in dominated_indices[p]:
                    domination_counts[q] -= 1
                    if domination_counts[q] == 0:
                        next_front.append(q)
            i += 1
            if next_front:
                fronts.append(next_front)
            else:
                break

        return [f for f in fronts if f]

    def _crowding_distance(
        self, front: list[int], pop_scores: list[tuple[float, float, float, float]]
    ) -> dict[int, float]:
        """Compute crowding distance for individuals in a front."""
        if len(front) <= 2:
            return {idx: float("inf") for idx in front}

        distances: dict[int, float] = {idx: 0.0 for idx in front}
        num_objectives = 4

        for m in range(num_objectives):
            # Sort front by objective m
            sorted_front = sorted(front, key=lambda idx: pop_scores[idx][m])
            distances[sorted_front[0]] = float("inf")
            distances[sorted_front[-1]] = float("inf")

            obj_min = pop_scores[sorted_front[0]][m]
            obj_max = pop_scores[sorted_front[-1]][m]
            norm = (obj_max - obj_min) if (obj_max - obj_min) > 1e-6 else 1.0

            for i in range(1, len(sorted_front) - 1):
                prev_score = pop_scores[sorted_front[i - 1]][m]
                next_score = pop_scores[sorted_front[i + 1]][m]
                distances[sorted_front[i]] += (next_score - prev_score) / norm

        return distances

    def evolve(
        self,
        target_vec: ParameterVector,
        base_preset: ParameterVector | None = None,
    ) -> list[tuple[ParameterVector, tuple[float, float, float, float]]]:
        """Execute the NSGA-II evolutionary search and return the non-dominated Pareto front."""
        base = base_preset or aksan_preset()
        population = self._init_population(target_vec, base)

        # Evolutionary loop
        for _ in range(self.generations):
            # 1. Evaluate current population
            pop_scores = [
                evaluate_objectives(ind, target_vec, base, self.validator)
                for ind in population
            ]

            # 2. Generate offspring (Q)
            offspring: list[ParameterVector] = []
            while len(offspring) < self.pop_size:
                # Tournament selection
                p1 = population[random.randint(0, len(population) - 1)]
                p2 = population[random.randint(0, len(population) - 1)]

                if random.random() < self.crossover_rate:
                    c1, c2 = self.crossover.cross(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                offspring.append(self.mutator.mutate(c1))
                if len(offspring) < self.pop_size:
                    offspring.append(self.mutator.mutate(c2))

            # 3. Combine Parents and Offspring (R = P U Q)
            combined_pop = population + offspring
            combined_scores = [
                evaluate_objectives(ind, target_vec, base, self.validator)
                for ind in combined_pop
            ]

            # 4. Non-dominated sort
            fronts = self._fast_non_dominated_sort(combined_scores)

            # 5. Elitist survival
            new_pop: list[ParameterVector] = []
            for front in fronts:
                if len(new_pop) + len(front) <= self.pop_size:
                    new_pop.extend(combined_pop[idx] for idx in front)
                else:
                    # Fill remaining slots using crowding distance
                    needed = self.pop_size - len(new_pop)
                    crowd_dist = self._crowding_distance(front, combined_scores)
                    sorted_by_crowd = sorted(
                        front, key=lambda idx: crowd_dist.get(idx, 0.0), reverse=True
                    )
                    new_pop.extend(combined_pop[idx] for idx in sorted_by_crowd[:needed])
                    break

            population = new_pop

        # Final evaluation of population and extraction of Front 1
        final_scores = [
            evaluate_objectives(ind, target_vec, base, self.validator)
            for ind in population
        ]
        fronts = self._fast_non_dominated_sort(final_scores)
        front_1_indices = fronts[0] if fronts else list(range(len(population)))

        pareto_front: list[tuple[ParameterVector, tuple[float, float, float, float]]] = [
            (population[i], final_scores[i]) for i in front_1_indices
        ]

        return pareto_front


def select_archetypes(
    pareto_candidates: list[tuple[ParameterVector, tuple[float, float, float, float]]],
    lyrics: str | None = None,
) -> list[ParetoArchetype]:
    """Extract 4 distinct representative archetypes from Pareto front candidates.

    Archetypes:
    1. The Purist (α): Maximum identity fidelity.
    2. The Rebel (β): Maximum intent / dramatic peak.
    3. The Avant-Garde (γ): Maximum novelty / modal exploration.
    4. The Knee-Point (δ): Balanced harmonic compromise.
    """
    if not pareto_candidates:
        fallback = aksan_preset()
        scores = (0.8, 1.0, 0.6, 1.0)
        pareto_candidates = [(fallback, scores)]

    suno_trans = SunoTranslator()
    lyria_trans = LyriaTranslator()
    map_builder = SectionMapBuilder()

    def format_archetype(
        name: str, arc_id: str, desc: str, vec: ParameterVector, scores: tuple[float, float, float, float]
    ) -> ParetoArchetype:
        suno_out = suno_trans.translate(vec, lyrics=lyrics, max_style_chars=1000)
        lyria_out = lyria_trans.translate(vec, lyrics=lyrics)
        sections = map_builder.build_from_vector(vec)
        map_str = f"{map_builder.format_map(sections)} [{map_builder.format_energy(sections)}]"

        return ParetoArchetype(
            name=name,
            archetype_id=arc_id,
            description=desc,
            vector=vec,
            scores=scores,
            suno_style=suno_out.style_prompt,
            lyria_narrative=lyria_out.narrative_prompt,
            section_map=map_str,
        )

    selected_indices: set[int] = set()

    def pick_best(metric_fn) -> tuple[ParameterVector, tuple[float, float, float, float]]:
        candidates = [
            (idx, c) for idx, c in enumerate(pareto_candidates)
            if idx not in selected_indices
        ]
        if not candidates:
            candidates = list(enumerate(pareto_candidates))
        best_idx, best_cand = max(candidates, key=lambda pair: metric_fn(pair[1]))
        selected_indices.add(best_idx)
        return best_cand

    # 1. The Purist: highest identity score (scores[1])
    purist_candidate = pick_best(lambda c: (c[1][1], c[1][3]))

    # 2. The Electronic Neoclassical / Intent: highest intent score (scores[0])
    intent_candidate = pick_best(lambda c: (c[1][0], c[1][3]))

    # 3. The Rebel: high tension, dramatic surge, and climax
    def rebel_metric(cand: tuple[ParameterVector, tuple[float, float, float, float]]) -> float:
        vec = cand[0]
        tension = int(vec.get(103)) if str(vec.get(103)).isdigit() else 3
        climax = int(vec.get(95)) if str(vec.get(95)).isdigit() else 3
        return cand[1][0] * 0.4 + (tension / 5.0) * 0.3 + (climax / 5.0) * 0.3

    rebel_candidate = pick_best(rebel_metric)

    # 4. The Avant-Garde: highest novelty score (scores[2])
    avant_candidate = pick_best(lambda c: (c[1][2], c[1][3]))

    # 5. The Knee-Point: balanced geometric product across all 4 objectives
    def balance_metric(cand: tuple[ParameterVector, tuple[float, float, float, float]]) -> float:
        s = cand[1]
        return s[0] * s[1] * (0.5 + s[2]) * (s[3] ** 2)

    knee_candidate = pick_best(balance_metric)

    return [
        format_archetype(
            name="The Purist",
            arc_id="alpha",
            desc="Maximum adherence to the canonical acoustic heritage (intimate, raw, zero electronic distractions).",
            vec=purist_candidate[0],
            scores=purist_candidate[1],
        ),
        format_archetype(
            name="The Electronic Neoclassical",
            arc_id="beta",
            desc="Focused on synthesized ambient textures: breathy bansuri lead, organ pedal pad, and marimba broken chords.",
            vec=intent_candidate[0],
            scores=intent_candidate[1],
        ),
        format_archetype(
            name="The Rebel",
            arc_id="gamma",
            desc="Maximum emotional tension: powerful dynamic surge, raw untamed wail in the bridge, and intense climax.",
            vec=rebel_candidate[0],
            scores=rebel_candidate[1],
        ),
        format_archetype(
            name="The Avant-Garde",
            arc_id="delta",
            desc="Experimental modal colorations, microtonal Kurdish intervals, asymmetric meter, and infinite cathedral decay.",
            vec=avant_candidate[0],
            scores=avant_candidate[1],
        ),
        format_archetype(
            name="The Knee-Point",
            arc_id="epsilon",
            desc="The optimal mathematical sweet spot balancing identity, intent, novelty, and rule compliance.",
            vec=knee_candidate[0],
            scores=knee_candidate[1],
        ),
    ]


def evolve(
    user_request: str | ParameterVector,
    base_preset: ParameterVector | None = None,
    lyrics: str | None = None,
    population_size: int = 20,
    generations: int = 10,
    seed: int | None = None,
) -> list[ParetoArchetype]:
    """High-level entry point to evolve and return 4 distinct Pareto archetypes."""
    # 1. Resolve target vector
    if isinstance(user_request, ParameterVector):
        target_vec = user_request
    else:
        # Generate initial fast baseline interpretation to seed the evolutionary search
        from composer160.engine.interpreter import Interpreter

        interpreter = Interpreter(preset=base_preset or aksan_preset())
        try:
            target_vec = interpreter.interpret_sync(user_request)
        except Exception:
            target_vec = (base_preset or aksan_preset()).copy()

    # 2. Run optimizer
    optimizer = ParetoOptimizer(
        population_size=population_size,
        generations=generations,
        seed=seed,
    )
    front = optimizer.evolve(target_vec=target_vec, base_preset=base_preset)

    # 3. Select the 4 archetypes
    return select_archetypes(front, lyrics=lyrics)
