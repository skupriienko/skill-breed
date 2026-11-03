"""Comprehensive unit, security, and stress tests for skill-breed."""

import time
import pytest
from pathlib import Path

from skill_breed.breed import (
    Allele,
    AlleleType,
    ChromosomeExtractor,
    HeterosisEvaluator,
    HybridMutationFuzzer,
    MAX_SKILL_FILE_BYTES,
    SkillBreeder,
    SkillChromosome,
    breed_skills,
    safe_resolve_path,
    sanitize_identifier,
)


def test_allele_serialization():
    a = Allele("scanner_ast", AlleleType.SENSOR, "Scans AST", weight=1.4, dominant=True)
    d = a.to_dict()
    assert d["name"] == "scanner_ast"
    assert d["kind"] == "sensor"
    assert d["dominant"] is True
    assert d["weight"] == 1.4


def test_sanitize_identifier():
    assert sanitize_identifier("my skill / danger! 123") == "my_skill_danger_123"
    assert sanitize_identifier("../../../etc/passwd") == "etc_passwd"
    assert sanitize_identifier("---") == "unnamed"


def test_chromosome_extraction():
    content = """---
name: code-impact
description: Scans blast radius of code changes
---
# Code Impact
Inspects AST. Invariant: Never allow breaking API shifts.
Decides migration plan. Emits patches.
"""
    chrom = ChromosomeExtractor.extract_from_text("code-impact", content)
    assert chrom.name == "code-impact"
    assert any(a.kind == AlleleType.INVARIANT for a in chrom.alleles)
    assert any(a.kind == AlleleType.SENSOR for a in chrom.alleles)
    assert any(a.kind == AlleleType.COGNITION for a in chrom.alleles)
    assert any(a.kind == AlleleType.ACTUATOR for a in chrom.alleles)


def test_breeding_meiosis_and_dag():
    breeder = SkillBreeder(threshold=1.10, seed=42)
    s1 = SkillChromosome(
        "sec-scanner",
        "security-governance",
        "Static checks",
        alleles=[
            Allele("audit_tokens", AlleleType.SENSOR, "Audit", weight=1.1),
            Allele("guard_secret", AlleleType.INVARIANT, "Block secret leaks", weight=2.0, dominant=True),
        ],
    )
    s2 = SkillChromosome(
        "git-flow",
        "lifecycle-process",
        "Git automation",
        alleles=[
            Allele("commit_push", AlleleType.ACTUATOR, "Pushes commits", weight=1.2),
            Allele("guard_branch", AlleleType.INVARIANT, "Clean branch", weight=2.0, dominant=True),
        ],
    )
    res = breeder.breed(s1, s2)
    assert res.passed_gate
    assert res.heterosis_score >= 1.10
    allele_names = [a.name for a in res.alleles]
    assert "guard_secret" in allele_names
    assert "guard_branch" in allele_names
    assert res.emergent_capabilities
    assert res.tool_chain_dag
    assert "edges" in res.tool_chain_dag


def test_mermaid_generation():
    breeder = SkillBreeder(threshold=1.05, seed=42)
    s1 = SkillChromosome("a", "alpha", "A", [Allele("s1", AlleleType.SENSOR, "S1")])
    s2 = SkillChromosome("b", "beta", "B", [Allele("a2", AlleleType.ACTUATOR, "A2")])
    res = breeder.breed(s1, s2)
    mermaid = res.to_mermaid()
    assert "flowchart LR" in mermaid
    assert "subgraph ParentA" in mermaid
    assert "subgraph Actuators" in mermaid


def test_security_oversized_file_rejection(tmp_path: Path):
    oversized_file = tmp_path / "SKILL.md"
    # Create file slightly exceeding MAX_SKILL_FILE_BYTES
    oversized_file.write_bytes(b"A" * (MAX_SKILL_FILE_BYTES + 1024))
    with pytest.raises(ValueError, match="exceeds maximum safety limit"):
        ChromosomeExtractor.load_skill_file(oversized_file)


def test_stress_high_throughput_breeding():
    """Breeds 1,000 hybrid skill combinations under 1.5 seconds."""
    breeder = SkillBreeder(threshold=1.05, seed=123)
    pool = [
        SkillChromosome(
            f"skill_{i}",
            f"domain_{i % 8}",
            f"Description for skill {i}",
            alleles=[
                Allele(f"s_{i}", AlleleType.SENSOR, "Sensing", weight=1.0),
                Allele(f"a_{i}", AlleleType.ACTUATOR, "Acting", weight=1.0),
                Allele(f"i_{i}", AlleleType.INVARIANT, "Guard", weight=2.0, dominant=True),
            ],
        )
        for i in range(40)
    ]

    t0 = time.perf_counter()
    total_bred = 0
    passed = 0
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            res = breeder.breed(pool[i], pool[j])
            total_bred += 1
            if res.passed_gate:
                passed += 1

    elapsed = time.perf_counter() - t0
    assert total_bred >= 780
    assert elapsed < 1.5, f"Stress test took too long: {elapsed:.2f}s"
    print(f"Bred {total_bred} skills in {elapsed:.3f}s ({total_bred / elapsed:.1f} ops/sec)")
