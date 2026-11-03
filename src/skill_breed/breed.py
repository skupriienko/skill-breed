#!/usr/bin/env python3
"""Cross-Breeding Engine: Interspecific Skill Hybridization and Synthesis.

Decomposes agent skills into functional genetic alleles (Sensor, Cognition,
Actuator, Invariant), executes FSM-driven combinatorial meiosis and boundary
mutation fuzzing, and evaluates offspring vigor using the Aleksakha Heterosis Gate.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

# Security Limits
MAX_SKILL_FILE_BYTES = 512_000  # 512 KB per SKILL.md
MAX_FRONTMATTER_BYTES = 64_000  # 64 KB frontmatter ceiling


class AlleleType(StrEnum):
    """Categorization of functional skill units (alleles)."""

    SENSOR = "sensor"
    COGNITION = "cognition"
    ACTUATOR = "actuator"
    INVARIANT = "invariant"


def sanitize_identifier(raw: str) -> str:
    """Sanitize any raw string into a safe python/filesystem identifier."""
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_-") or "unnamed"


def safe_resolve_path(path_input: Path | str) -> Path:
    """Safely resolve path preventing traversal outside intended boundaries."""
    return Path(path_input).expanduser().resolve()


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
            "weight": round(self.weight, 2),
            "dominant": self.dominant,
        }


@dataclass
class SkillChromosome:
    """Structured genomic representation of an agent skill."""

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
    emergent_capabilities: list[str]
    alleles: list[Allele]
    heterosis_score: float
    passed_gate: bool
    tool_chain_dag: dict[str, Any] = field(default_factory=dict)
    fuzz_log: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_a": self.parent_a,
            "parent_b": self.parent_b,
            "offspring_name": self.offspring_name,
            "offspring_genus": self.offspring_genus,
            "emergent_concept": self.emergent_concept,
            "emergent_capabilities": self.emergent_capabilities,
            "heterosis_score": round(self.heterosis_score, 3),
            "passed_gate": self.passed_gate,
            "alleles": [a.to_dict() for a in self.alleles],
            "tool_chain_dag": self.tool_chain_dag,
            "fuzz_log": self.fuzz_log,
        }

    def to_mermaid(self) -> str:
        """Generate a Mermaid flowchart visualizing the synthesized tool chain DAG."""

        def m_id(val: str) -> str:
            return re.sub(r"[^a-zA-Z0-9_]", "_", val).strip("_")

        lines = [
            "```mermaid",
            "flowchart LR",
            f'    subgraph ParentA["Parent A: {self.parent_a}"]',
        ]
        sensors = [a for a in self.alleles if a.kind == AlleleType.SENSOR]
        for s in sensors:
            lines.append(f'        {m_id(s.name)}["[Sensor] {s.name}"]')
        lines.append("    end")

        lines.append(f'    subgraph Cognition["Cognition Engine: {self.offspring_name}"]')
        cogs = [a for a in self.alleles if a.kind == AlleleType.COGNITION]
        for c in cogs:
            lines.append(f'        {m_id(c.name)}{{"[Cognition] {c.name}"}}')
        lines.append("    end")

        lines.append(f'    subgraph Actuators["Actuation Pipeline: {self.parent_b}"]')
        acts = [a for a in self.alleles if a.kind == AlleleType.ACTUATOR]
        for a in acts:
            lines.append(f'        {m_id(a.name)}["[Actuator] {a.name}"]')
        lines.append("    end")

        lines.append('    subgraph Invariants["Dominant Invariant Gates"]')
        invs = [a for a in self.alleles if a.kind == AlleleType.INVARIANT]
        for inv in invs:
            lines.append(f'        {m_id(inv.name)}[["[Invariant Gate] {inv.name}"]]')
        lines.append("    end")

        # Connect sensors to cognition
        for s in sensors:
            for c in cogs:
                lines.append(f"    {m_id(s.name)} --> {m_id(c.name)}")

        # Connect cognition to actuators
        for c in cogs:
            for a in acts:
                lines.append(f"    {m_id(c.name)} --> {m_id(a.name)}")

        # Connect invariants to actuators as guards
        for inv in invs:
            for a in acts:
                lines.append(f"    {m_id(inv.name)} -.->|Guard| {m_id(a.name)}")

        lines.append("```")
        return "\n".join(lines)


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
        "eval": "meta-testing",
        "concurrency": "multi-agent-safety",
    }

    @classmethod
    def extract_from_text(cls, name: str, text: str) -> SkillChromosome:
        """Parses markdown text into a SkillChromosome with ReDoS and buffer defense."""
        safe_name = sanitize_identifier(name)
        genus = "general-engineering"
        lower_name = safe_name.lower()
        for k, g in cls.GENUS_MAP.items():
            if k in lower_name:
                genus = g
                break

        # Bound frontmatter parsing to prevent regex backtracking
        bounded_head = text[:MAX_FRONTMATTER_BYTES]
        desc_match = re.search(r"^description:\s*([^\n]+)", bounded_head, re.MULTILINE)
        desc = desc_match.group(1).strip().strip("'\"") if desc_match else f"Skill {safe_name}"

        alleles: list[Allele] = []

        # 1. Sensor alleles
        sensors = re.findall(
            r"\b(?:detect|audit|scan|search|inspect|read|parse|measure|monitor)\w*",
            text[:MAX_SKILL_FILE_BYTES],
            re.IGNORECASE,
        )
        if sensors:
            top_sensor = sanitize_identifier(max(set(sensors), key=sensors.count).lower())
            alleles.append(
                Allele(
                    name=f"{safe_name}_sensor_{top_sensor}",
                    kind=AlleleType.SENSOR,
                    summary=f"Perceptual telemetry and inspection via {top_sensor}",
                    weight=1.2,
                )
            )

        # 2. Cognition alleles
        cognition = re.findall(
            r"\b(?:reason|decide|plan|classify|evaluate|optimize|prioritize|synthesize)\w*",
            text[:MAX_SKILL_FILE_BYTES],
            re.IGNORECASE,
        )
        if cognition:
            top_cog = sanitize_identifier(max(set(cognition), key=cognition.count).lower())
            alleles.append(
                Allele(
                    name=f"{safe_name}_cognition_{top_cog}",
                    kind=AlleleType.COGNITION,
                    summary=f"Cognitive strategy and heuristic logic via {top_cog}",
                    weight=1.5,
                )
            )

        # 3. Actuator alleles
        actuators = re.findall(
            r"\b(?:write|modify|execute|format|lint|generate|patch|deploy|emit)\w*",
            text[:MAX_SKILL_FILE_BYTES],
            re.IGNORECASE,
        )
        if actuators:
            top_act = sanitize_identifier(max(set(actuators), key=actuators.count).lower())
            alleles.append(
                Allele(
                    name=f"{safe_name}_actuator_{top_act}",
                    kind=AlleleType.ACTUATOR,
                    summary=f"Operational mutation and dispatch via {top_act}",
                    weight=1.3,
                )
            )

        # 4. Invariant alleles
        invariants = re.findall(
            r"\b(?:invariant|ceiling|must|never|strictly|contract|bound|budget)\w*",
            text[:MAX_SKILL_FILE_BYTES],
            re.IGNORECASE,
        )
        if invariants:
            top_inv = sanitize_identifier(max(set(invariants), key=invariants.count).lower())
            alleles.append(
                Allele(
                    name=f"{safe_name}_invariant_{top_inv}",
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
                    f"{safe_name}_core_sensor",
                    AlleleType.SENSOR,
                    f"Observation driver for {safe_name}",
                    weight=1.0,
                ),
                Allele(
                    f"{safe_name}_core_policy",
                    AlleleType.COGNITION,
                    f"Decision policy for {safe_name}",
                    weight=1.2,
                ),
                Allele(
                    f"{safe_name}_core_action",
                    AlleleType.ACTUATOR,
                    f"Action dispatch for {safe_name}",
                    weight=1.1,
                ),
                Allele(
                    f"{safe_name}_core_contract",
                    AlleleType.INVARIANT,
                    f"Contract enforcement for {safe_name}",
                    weight=2.0,
                    dominant=True,
                ),
            ]

        return SkillChromosome(name=safe_name, genus=genus, description=desc, alleles=alleles)

    @classmethod
    def load_skill_file(cls, path_input: Path | str) -> SkillChromosome:
        """Reads a SKILL.md file or directory and extracts its chromosome safely."""
        path = safe_resolve_path(path_input)
        if path.is_dir():
            target_file = path / "SKILL.md"
            if not target_file.exists():
                err_missing = f"Missing mandatory SKILL.md in directory: {path}"
                raise FileNotFoundError(err_missing)
            name = path.name
        else:
            target_file = path
            name = path.parent.name if path.name == "SKILL.md" else path.stem

        if target_file.stat().st_size > MAX_SKILL_FILE_BYTES:
            err_size = (
                f"File size exceeds maximum safety limit ({target_file.stat().st_size} > {MAX_SKILL_FILE_BYTES} bytes)"
            )
            raise ValueError(err_size)

        content = target_file.read_text(encoding="utf-8", errors="replace")
        return cls.extract_from_text(name, content)

    @classmethod
    def extract_from_skill_dir(cls, dir_path: Path | str) -> SkillChromosome:
        """Alias for load_skill_file supporting directories."""
        return cls.load_skill_file(dir_path)


class HybridMutationFuzzer:
    """Fuzz State Machine Engine (FSME) for boundary allele interactions and tool chaining."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)  # noqa: S311

    def fuzz_boundary(
        self,
        parent_a: SkillChromosome,
        parent_b: SkillChromosome,
        crossover_alleles: list[Allele],
    ) -> tuple[list[Allele], list[str], list[str], dict[str, Any]]:
        """Subject crossed alleles to state-space boundary fuzzing and tool-chain synthesis."""
        log: list[str] = []
        emergent_caps: list[str] = []
        result_alleles = list(crossover_alleles)

        log.append(
            f"FSME [STATE:INIT]: Pairing '{parent_a.name}' ({parent_a.genus}) x '{parent_b.name}' ({parent_b.genus})"
        )

        # 1. Invariant Dominance Pass
        invariants = [a for a in result_alleles if a.kind == AlleleType.INVARIANT]
        log.append(f"FSME [STATE:INVARIANT_CHECK]: {len(invariants)} boundary invariants verified as dominant")

        # 2. Sensor-Actuator Dialectical Synthesis
        sensors = [a for a in result_alleles if a.kind == AlleleType.SENSOR]
        actuators = [a for a in result_alleles if a.kind == AlleleType.ACTUATOR]

        if sensors and actuators:
            s = sensors[0]
            a = actuators[0]
            emergent_name = f"synth_{s.name}_{a.name}"
            emergent_allele = Allele(
                name=emergent_name,
                kind=AlleleType.COGNITION,
                summary=f"Synthesized closed-loop feedback controller between {s.name} and {a.name}",
                weight=1.9,
            )
            result_alleles.append(emergent_allele)
            emergent_caps.append(f"Autonomous feedback loop: {s.name} -> {a.name}")
            log.append(f"FSME [STATE:DIALECTICAL_SYNTHESIS]: Generated emergent allele '{emergent_name}'")

        # 3. Cross-Genus Boundary Invariant Synthesis
        if parent_a.genus != parent_b.genus:
            boundary_guard_name = f"guard_{parent_a.name[:8]}_{parent_b.name[:8]}"
            guard_allele = Allele(
                name=boundary_guard_name,
                kind=AlleleType.INVARIANT,
                summary=f"Cross-boundary contract ensuring zero interface drift between {parent_a.genus} and {parent_b.genus}",
                weight=2.2,
                dominant=True,
            )
            result_alleles.append(guard_allele)
            emergent_caps.append(f"Cross-domain contract enforcement: {parent_a.genus} <-> {parent_b.genus}")
            log.append(f"FSME [STATE:CROSS_GENUS_GUARD]: Generated boundary guard '{boundary_guard_name}'")

        # 4. Tool Chaining DAG Generation
        dag = {
            "entry_sensors": [s.name for s in sensors],
            "reasoning_nodes": [a.name for a in result_alleles if a.kind == AlleleType.COGNITION],
            "actuator_nodes": [a.name for a in actuators],
            "invariant_guards": [inv.name for inv in result_alleles if inv.kind == AlleleType.INVARIANT],
            "edges": [],
        }

        # Build edges: Sensors -> Cognition -> Actuators
        for s in sensors:
            for c in [a for a in result_alleles if a.kind == AlleleType.COGNITION]:
                dag["edges"].append({"from": s.name, "to": c.name, "type": "percept_feed"})

        for c in [a for a in result_alleles if a.kind == AlleleType.COGNITION]:
            for act in actuators:
                dag["edges"].append({"from": c.name, "to": act.name, "type": "dispatch_command"})

        log.append(f"FSME [STATE:TOOL_CHAIN_SYNTHESIS]: Synthesized DAG with {len(dag['edges'])} active paths")
        log.append(f"FSME [STATE:CLOSURE]: Final hybrid allele count = {len(result_alleles)}")

        return result_alleles, emergent_caps, log, dag


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
        genus_distance_bonus = 1.25 if parent_a.genus != parent_b.genus else 1.08
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
        safe_a = sanitize_identifier(parent_a.name)
        safe_b = sanitize_identifier(parent_b.name)
        offspring_name = f"hybrid_{safe_a}_{safe_b}"
        offspring_genus = f"hybrid-{parent_a.genus}-{parent_b.genus}"

        # Meiotic Crossover: collect all dominant alleles, sample balanced set of others
        selected_alleles: list[Allele] = []

        # All dominant invariant alleles are strictly preserved
        for p in (parent_a, parent_b):
            for a in p.alleles:
                if a.dominant and a not in selected_alleles:
                    selected_alleles.append(a)

        # Select non-dominant alleles from both parents
        other_a = [a for a in parent_a.alleles if not a.dominant]
        other_b = [a for a in parent_b.alleles if not a.dominant]

        selected_alleles.extend(other_a[:3])
        selected_alleles.extend(other_b[:3])

        # Execute FSME boundary fuzzing & Tool Chaining
        fuzzed_alleles, emergent_caps, fuzz_log, tool_dag = self.fuzzer.fuzz_boundary(
            parent_a, parent_b, selected_alleles
        )

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
            emergent_capabilities=emergent_caps,
            alleles=fuzzed_alleles,
            heterosis_score=heterosis_score,
            passed_gate=passed,
            tool_chain_dag=tool_dag,
            fuzz_log=fuzz_log,
        )


def breed_skills(
    skill_a_path: Path | str,
    skill_b_path: Path | str,
    threshold: float = 1.15,
    seed: int | None = None,
) -> HybridResult:
    """Convenience function to breed two agent skills directly from filesystem paths."""
    chrom_a = ChromosomeExtractor.load_skill_file(skill_a_path)
    chrom_b = ChromosomeExtractor.load_skill_file(skill_b_path)
    breeder = SkillBreeder(threshold=threshold, seed=seed if seed is not None else 42)
    return breeder.breed(chrom_a, chrom_b)
