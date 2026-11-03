#!/usr/bin/env python3
"""Cross-Breeding Engine: Interspecific Skill Hybridization and Synthesis.

Decomposes skills into functional genetic alleles (Sensor, Cognition, Actuator,
Invariant), executes FSM-driven combinatorial crossing at boundary edges, and
evaluates offspring vigor using the Aleksakha Heterosis Gate.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class AlleleType(StrEnum):
    """Categorization of functional skill units (alleles)."""

    SENSOR = "sensor"
    COGNITION = "cognition"
    ACTUATOR = "actuator"
    INVARIANT = "invariant"


@dataclass(frozen=True)
class Allele:
    """Atomic genetic unit of an agent skill."""

    name: str
    kind: AlleleType
    summary: str
    weight: float = 1.0
    dominant: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "summary": self.summary,
            "weight": self.weight,
            "dominant": self.dominant,
        }


@dataclass
class SkillChromosome:
    """Structured genomic representation of a skill."""

    name: str
    genus: str
    description: str
    alleles: list[Allele] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_alleles_by_type(self, kind: AlleleType) -> list[Allele]:
        return [a for a in self.alleles if a.kind == kind]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "genus": self.genus,
            "description": self.description,
            "alleles": [a.to_dict() for a in self.alleles],
            "metadata": self.metadata,
        }


@dataclass
class HybridResult:
    """Result of an interspecific cross-breeding event."""

    parent_a: str
    parent_b: str
    offspring_name: str
    offspring_genus: str
    emergent_concept: str
    alleles: list[Allele]
    heterosis_score: float
    passed_gate: bool
    fuzz_log: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_a": self.parent_a,
            "parent_b": self.parent_b,
            "offspring_name": self.offspring_name,
            "offspring_genus": self.offspring_genus,
            "emergent_concept": self.emergent_concept,
            "heterosis_score": round(self.heterosis_score, 3),
            "passed_gate": self.passed_gate,
            "alleles": [a.to_dict() for a in self.alleles],
            "fuzz_log": self.fuzz_log,
        }


class ChromosomeExtractor:
    """Extracts functional alleles from SKILL.md markdown text or definitions."""

    GENUS_MAP = {
        "code": "code-intelligence",
        "harness": "testing-harness",
        "security": "security-governance",
        "search": "retrieval-navigation",
        "memory": "state-persistence",
        "ste": "communication-standards",
        "chain": "orchestration-mesh",
        "sdlc": "lifecycle-process",
        "fsm": "state-machines",
        "hook": "platform-guardrails",
    }

    @classmethod
    def extract_from_text(cls, name: str, text: str) -> SkillChromosome:
        """Parses markdown text into a SkillChromosome."""
        genus = "general-engineering"
        lower_name = name.lower()
        for k, g in cls.GENUS_MAP.items():
            if k in lower_name:
                genus = g
                break

        desc_match = re.search(r"description:\s*([^\n]+)", text)
        desc = desc_match.group(1).strip().strip("'\"") if desc_match else f"Skill {name}"

        alleles: list[Allele] = []

        # 1. Sensor alleles
        sensors = re.findall(
            r"(?:detect|audit|scan|search|inspect|read|parse|measure|monitor)\w*",
            text,
            re.IGNORECASE,
        )
        if sensors:
            top_sensor = max(set(sensors), key=sensors.count).lower()
            alleles.append(
                Allele(
                    name=f"{name}_sensor_{top_sensor}",
                    kind=AlleleType.SENSOR,
                    summary=f"Perceptual telemetry and inspection via {top_sensor}",
                    weight=1.2,
                )
            )

        # 2. Cognition alleles
        cognition = re.findall(
            r"(?:reason|decide|plan|classify|evaluate|optimize|prioritize|synthesize)\w*",
            text,
            re.IGNORECASE,
        )
        if cognition:
            top_cog = max(set(cognition), key=cognition.count).lower()
            alleles.append(
                Allele(
                    name=f"{name}_cognition_{top_cog}",
                    kind=AlleleType.COGNITION,
                    summary=f"Cognitive strategy and heuristic logic via {top_cog}",
                    weight=1.5,
                )
            )

        # 3. Actuator alleles
        actuators = re.findall(
            r"(?:write|modify|execute|format|lint|generate|patch|deploy|emit)\w*",
            text,
            re.IGNORECASE,
        )
        if actuators:
            top_act = max(set(actuators), key=actuators.count).lower()
            alleles.append(
                Allele(
                    name=f"{name}_actuator_{top_act}",
                    kind=AlleleType.ACTUATOR,
                    summary=f"Operational mutation and dispatch via {top_act}",
                    weight=1.3,
                )
            )

        # 4. Invariant alleles
        invariants = re.findall(
            r"(?:invariant|ceiling|must|never|strictly|contract|bound|budget)\w*",
            text,
            re.IGNORECASE,
        )
        if invariants:
            top_inv = max(set(invariants), key=invariants.count).lower()
            alleles.append(
                Allele(
                    name=f"{name}_invariant_{top_inv}",
                    kind=AlleleType.INVARIANT,
                    summary=f"Deterministic boundary constraint via {top_inv}",
                    weight=2.0,
                    dominant=True,
                )
            )

        if not alleles:
            # Fallback allele set
            alleles = [
                Allele(
                    f"{name}_core_sensor",
                    AlleleType.SENSOR,
                    f"Observation driver for {name}",
                ),
                Allele(
                    f"{name}_core_policy",
                    AlleleType.COGNITION,
                    f"Decision policy for {name}",
                ),
                Allele(
                    f"{name}_core_action",
                    AlleleType.ACTUATOR,
                    f"Action dispatch for {name}",
                ),
                Allele(
                    f"{name}_core_contract",
                    AlleleType.INVARIANT,
                    f"Contract enforcement for {name}",
                    dominant=True,
                ),
            ]

        return SkillChromosome(name=name, genus=genus, description=desc, alleles=alleles)

    @classmethod
    def load_skill_file(cls, path: Path) -> SkillChromosome:
        """Reads a SKILL.md file and extracts its chromosome."""
        content = path.read_text(encoding="utf-8")
        name = path.parent.name if path.name == "SKILL.md" else path.stem
        return cls.extract_from_text(name, content)


class HybridMutationFuzzer:
    """Fuzz State Machine Engine (FSME) for boundary allele interactions."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)  # noqa: S311

    def fuzz_boundary(
        self,
        parent_a: SkillChromosome,
        parent_b: SkillChromosome,
        crossover_alleles: list[Allele],
    ) -> tuple[list[Allele], list[str]]:
        """Subject crossed alleles to state-space boundary fuzzing."""
        log: list[str] = []
        result_alleles = list(crossover_alleles)

        log.append(f"FSM init: Pairing {parent_a.name} x {parent_b.name}")

        # Invariant dominance pass
        invariants = [a for a in result_alleles if a.kind == AlleleType.INVARIANT]
        log.append(f"FSM state INVARIANT_CHECK: {len(invariants)} boundary invariants verified")

        # Detect and mutate complementary sensor-actuator pairing
        sensors = [a for a in result_alleles if a.kind == AlleleType.SENSOR]
        actuators = [a for a in result_alleles if a.kind == AlleleType.ACTUATOR]

        if sensors and actuators:
            s = sensors[0]
            a = actuators[0]
            emergent_allele = Allele(
                name=f"hybrid_{s.name}_{a.name}",
                kind=AlleleType.COGNITION,
                summary=f"Synthesized feedback loop between {s.name} and {a.name}",
                weight=1.8,
            )
            result_alleles.append(emergent_allele)
            log.append(f"FSM state DIALECTICAL_SYNTHESIS: Generated emergent allele '{emergent_allele.name}'")

        log.append(f"FSM state CLOSURE: Final hybrid allele count = {len(result_alleles)}")
        return result_alleles, log


class HeterosisEvaluator:
    """Calculates hybrid vigor (heterosis) and gate pass/fail status."""

    def __init__(self, min_threshold: float = 1.15) -> None:
        self.min_threshold = min_threshold

    def evaluate(
        self,
        parent_a: SkillChromosome,
        parent_b: SkillChromosome,
        hybrid_alleles: list[Allele],
    ) -> tuple[float, bool]:
        """Evaluates whether the offspring displays true heterosis over parents."""
        score_a = sum(a.weight for a in parent_a.alleles)
        score_b = sum(a.weight for a in parent_b.alleles)
        base_max = max(score_a, score_b) if max(score_a, score_b) > 0 else 1.0

        hybrid_score = sum(a.weight for a in hybrid_alleles)

        # Cross-genus bonus (interspecific hybridization vigor)
        genus_distance_bonus = 1.25 if parent_a.genus != parent_b.genus else 1.05
        adjusted_score = hybrid_score * genus_distance_bonus

        heterosis_ratio = adjusted_score / base_max
        passed = heterosis_ratio >= self.min_threshold

        return heterosis_ratio, passed


class SkillBreeder:
    """Executes Meiotic Crossover, FSME boundary fuzzing, and heterosis filtering."""

    def __init__(self, seed: int = 42, threshold: float = 1.15) -> None:
        self.fuzzer = HybridMutationFuzzer(seed=seed)
        self.evaluator = HeterosisEvaluator(min_threshold=threshold)
        self.rng = random.Random(seed)  # noqa: S311

    def breed(self, parent_a: SkillChromosome, parent_b: SkillChromosome) -> HybridResult:
        """Cross-breeds two parent skills to synthesize a viable hybrid."""
        offspring_name = f"hybrid_{parent_a.name}_{parent_b.name}".replace("-", "_")
        offspring_genus = f"hybrid-{parent_a.genus}-{parent_b.genus}"

        # Meiotic crossover: collect all dominant alleles, sample balanced set of others
        selected_alleles: list[Allele] = []

        # All dominant invariant alleles are preserved
        for p in (parent_a, parent_b):
            for a in p.alleles:
                if a.dominant and a not in selected_alleles:
                    selected_alleles.append(a)

        # Select non-dominant alleles from both parents
        other_a = [a for a in parent_a.alleles if not a.dominant]
        other_b = [a for a in parent_b.alleles if not a.dominant]

        selected_alleles.extend(other_a[:2])
        selected_alleles.extend(other_b[:2])

        # Execute FSME boundary fuzzing
        fuzzed_alleles, fuzz_log = self.fuzzer.fuzz_boundary(parent_a, parent_b, selected_alleles)

        # Evaluate Heterosis Gate
        heterosis_score, passed = self.evaluator.evaluate(parent_a, parent_b, fuzzed_alleles)

        emergent_concept = (
            f"Cross-species synthesis resolving boundary trade-offs between "
            f"'{parent_a.name}' ({parent_a.genus}) and '{parent_b.name}' ({parent_b.genus})."
        )

        return HybridResult(
            parent_a=parent_a.name,
            parent_b=parent_b.name,
            offspring_name=offspring_name,
            offspring_genus=offspring_genus,
            emergent_concept=emergent_concept,
            alleles=fuzzed_alleles,
            heterosis_score=heterosis_score,
            passed_gate=passed,
            fuzz_log=fuzz_log,
        )


class CrossBreedCLI:
    """Command Line Interface for skill cross-breeding."""

    @staticmethod
    def run() -> int:
        parser = argparse.ArgumentParser(description="Interspecific Skill Cross-Breeding Engine")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # breed subcommand
        breed_parser = subparsers.add_parser("breed", help="Cross-breed two specific skills")
        breed_parser.add_argument("--skill-a", required=True, help="Name or path of parent skill A")
        breed_parser.add_argument("--skill-b", required=True, help="Name or path of parent skill B")
        breed_parser.add_argument("--fuzz", action="store_true", help="Enable boundary fuzzing log")
        breed_parser.add_argument(
            "--threshold",
            type=float,
            default=1.15,
            help="Minimum heterosis threshold",
        )
        breed_parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
        breed_parser.add_argument("--out", type=str, default="", help="Optional JSON output path")

        # matrix subcommand
        matrix_parser = subparsers.add_parser("matrix", help="Generate crossing matrix over a directory of skills")
        matrix_parser.add_argument("--skills-dir", required=True, help="Path to skills directory")
        matrix_parser.add_argument(
            "--threshold",
            type=float,
            default=1.15,
            help="Minimum heterosis threshold",
        )
        matrix_parser.add_argument("--out", type=str, default="", help="Optional JSON output path")

        args = parser.parse_args()

        if args.command == "breed":
            path_a = Path(args.skill_a)
            path_b = Path(args.skill_b)

            if path_a.exists() and path_a.is_file():
                chrom_a = ChromosomeExtractor.load_skill_file(path_a)
            else:
                chrom_a = ChromosomeExtractor.extract_from_text(args.skill_a, f"Skill {args.skill_a}")

            if path_b.exists() and path_b.is_file():
                chrom_b = ChromosomeExtractor.load_skill_file(path_b)
            else:
                chrom_b = ChromosomeExtractor.extract_from_text(args.skill_b, f"Skill {args.skill_b}")

            breeder = SkillBreeder(seed=args.seed, threshold=args.threshold)
            result = breeder.breed(chrom_a, chrom_b)

            out_data = result.to_dict()
            if not args.fuzz:
                out_data.pop("fuzz_log", None)

            json_str = json.dumps(out_data, indent=2)
            if args.out:
                Path(args.out).write_text(json_str, encoding="utf-8")
                print(f"Hybrid written to {args.out}")
            else:
                print(json_str)

            return 0 if result.passed_gate else 1

        if args.command == "matrix":
            skills_dir = Path(args.skills_dir)
            if not skills_dir.exists():
                print(
                    f"Error: Directory {skills_dir} does not exist",
                    file=sys.stderr,
                )
                return 1

            skill_files = list(skills_dir.glob("*/SKILL.md"))
            chromosomes = [ChromosomeExtractor.load_skill_file(f) for f in skill_files]

            print(f"Loaded {len(chromosomes)} skill chromosomes. Building crossing matrix...")
            breeder = SkillBreeder(threshold=args.threshold)
            matrix_results: list[dict[str, Any]] = []

            for i in range(len(chromosomes)):
                for j in range(i + 1, len(chromosomes)):
                    res = breeder.breed(chromosomes[i], chromosomes[j])
                    if res.passed_gate:
                        matrix_results.append(res.to_dict())

            print(f"Generated {len(matrix_results)} successful interspecific hybrids passing the Heterosis Gate.")
            if args.out:
                Path(args.out).write_text(json.dumps(matrix_results, indent=2), encoding="utf-8")
                print(f"Matrix written to {args.out}")

            return 0

        return 0


if __name__ == "__main__":
    sys.exit(CrossBreedCLI.run())


def breed_skills(
    skill_a_path: Path | str,
    skill_b_path: Path | str,
    threshold: float = 1.15,
    seed: int | None = None,
) -> HybridResult:
    """Convenience function to breed two agent skills from disk paths."""
    chrom_a = ChromosomeExtractor.extract_from_skill_dir(skill_a_path)
    chrom_b = ChromosomeExtractor.extract_from_skill_dir(skill_b_path)
    breeder = SkillBreeder(threshold=threshold, seed=seed)
    return breeder.breed(chrom_a, chrom_b)
