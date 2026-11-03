"""Stress tests and unit tests for skill-breed."""

import time
from pathlib import Path

from skill_breed.breed import (
    Allele,
    AlleleType,
    ChromosomeExtractor,
    HeterosisEvaluator,
    HybridMutationFuzzer,
    SkillBreeder,
    SkillChromosome,
    breed_skills,
)


def test_allele_serialization():
    a = Allele("scanner_ast", AlleleType.SENSOR, "Scans AST", weight=1.4, dominant=True)
    d = a.to_dict()
    assert d["name"] == "scanner_ast"
    assert d["kind"] == "sensor"
    assert d["dominant"] is True


def test_chromosome_extraction():
    content = """---
name: code-impact
description: Scans blast radius
---
# Code Impact
Inspects AST. Invariant: Never allow breaking API shifts.
"""
    chrom = ChromosomeExtractor.extract_from_text("code-impact", content)
    assert chrom.name == "code-impact"
    assert any(a.kind == AlleleType.INVARIANT for a in chrom.alleles)


def test_breeding_meiosis():
    breeder = SkillBreeder(threshold=1.10, seed=42)
    s1 = SkillChromosome(
        "sec-scanner",
        "security",
        "Static checks",
        alleles=[
            Allele("audit_tokens", AlleleType.SENSOR, "Audit", weight=1.1),
            Allele("guard_secret", AlleleType.INVARIANT, "Block secret leaks", weight=2.0, dominant=True),
        ],
    )
    s2 = SkillChromosome(
        "git-flow",
        "workflow",
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
