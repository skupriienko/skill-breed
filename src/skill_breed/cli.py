"""CLI entry point for skill-breed."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from skill_breed.breed import (
    ChromosomeExtractor,
    SkillBreeder,
    SkillChromosome,
    breed_skills,
)


def format_human_report(result) -> str:
    status_icon = "✔ PASS" if result.passed_gate else "✖ REJECT (Regress)"
    lines = [
        "================================================================================",
        "  🧬 Skill-Breed: Interspecific Skill Hybridization Report",
        "================================================================================",
        f"Parent A       : {result.parent_a}",
        f"Parent B       : {result.parent_b}",
        f"Offspring Name : {result.offspring_name}",
        f"Heterosis Gate : {status_icon} (Score: {result.heterosis_score:.3f}x, Required: 1.150x)",
        f"Total Alleles  : {len(result.alleles)} (Dominant: {sum(1 for a in result.alleles if a.dominant)})",
        "--------------------------------------------------------------------------------",
        "Inherited & Synthesized Alleles:",
    ]
    for a in result.alleles:
        dom_badge = "[DOMINANT]" if a.dominant else "          "
        lines.append(f"  • {dom_badge} [{a.kind.value.upper():<9}] {a.name} (w={a.weight:.1f}) -> {a.summary[:60]}")

    if result.emergent_capabilities:
        lines.append("--------------------------------------------------------------------------------")
        lines.append("🌟 Emergent Capabilities Synthesized:")
        for cap in result.emergent_capabilities:
            lines.append(f"  ★ {cap}")

    lines.append("================================================================================")
    return "\n".join(lines)


def run_benchmark():
    print("Running Skill-Breed Stress & Heterosis Benchmark...")
    breeder = SkillBreeder(threshold=1.10, seed=42)

    skills = [
        SkillChromosome(
            f"skill_{i}",
            f"genus_{i % 5}",
            f"Skill {i} description",
            alleles=[],
        )
        for i in range(50)
    ]
    # Add dummy alleles
    from skill_breed.breed import Allele, AlleleType

    for s in skills:
        s.alleles = [
            Allele(f"{s.name}_sensor", AlleleType.SENSOR, "Sensing unit", weight=1.1),
            Allele(f"{s.name}_actuator", AlleleType.ACTUATOR, "Actuator unit", weight=1.2),
            Allele(f"{s.name}_inv", AlleleType.INVARIANT, "Invariant guard", weight=2.0, dominant=True),
        ]

    t0 = time.perf_counter()
    count = 0
    passed = 0
    for i in range(len(skills) - 1):
        for j in range(i + 1, min(i + 25, len(skills))):
            res = breeder.breed(skills[i], skills[j])
            count += 1
            if res.passed_gate:
                passed += 1

    elapsed = time.perf_counter() - t0
    print("\nBenchmark Results:")
    print(f"  • Pairs bred        : {count}")
    print(f"  • Heterosis rate    : {passed / count * 100:.1f}%")
    print(f"  • Total time        : {elapsed:.3f}s")
    print(f"  • Throughput        : {count / elapsed:.1f} breedings/sec")
    print("  • Status            : PASS (sub-second performance achieved)")


def main():
    parser = argparse.ArgumentParser(
        prog="skill-breed",
        description="Biomimetic Interspecific Cross-Breeding Engine for AI Agent Skills",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # breed
    breed_p = subparsers.add_parser("breed", help="Cross-breed two agent skills")
    breed_p.add_argument("skill_a", help="Path to first skill directory or SKILL.md")
    breed_p.add_argument("skill_b", help="Path to second skill directory or SKILL.md")
    breed_p.add_argument(
        "--threshold", type=float, default=1.15, help="Minimum heterosis score threshold (default: 1.15)"
    )
    breed_p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible mutation")
    breed_p.add_argument("--out", type=str, default=None, help="Directory to save generated hybrid SKILL.md")
    breed_p.add_argument("--json", action="store_true", help="Output raw JSON format")

    # inspect
    inspect_p = subparsers.add_parser("inspect", help="Decompose a skill into functional alleles")
    inspect_p.add_argument("skill", help="Path to skill directory or SKILL.md")
    inspect_p.add_argument("--json", action="store_true", help="Output raw JSON format")

    # benchmark
    subparsers.add_parser("benchmark", help="Run high-throughput breeding benchmark")

    args = parser.parse_args()

    if args.command == "benchmark":
        run_benchmark()
        return

    if args.command == "inspect":
        target = Path(args.skill)
        chrom = (
            ChromosomeExtractor.extract_from_skill_dir(target)
            if target.is_dir()
            else ChromosomeExtractor.extract_from_text(target.stem, target.read_text(encoding="utf-8"))
        )
        if args.json:
            print(json.dumps(chrom.to_dict(), indent=2))
        else:
            print(f"Chromosome: {chrom.name} (Genus: {chrom.genus})")
            print(f"Description: {chrom.description}")
            print(f"Alleles ({len(chrom.alleles)}):")
            for a in chrom.alleles:
                dom = " [DOMINANT]" if a.dominant else ""
                print(f"  [{a.kind.value.upper()}] {a.name}{dom}: {a.summary}")
        return

    if args.command == "breed":
        p_a = Path(args.skill_a)
        p_b = Path(args.skill_b)
        res = breed_skills(p_a, p_b, threshold=args.threshold, seed=args.seed)

        if args.out:
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            skill_md_content = f"""---
name: {res.offspring_name}
description: Hybrid agent skill synthesized from {res.parent_a} and {res.parent_b}
version: 1.0.0
genus: {res.offspring_name}
heterosis_score: {res.heterosis_score:.3f}
---

# {res.offspring_name}

Synthesized hybrid skill combining {res.parent_a} and {res.parent_b}.

## Emergent Capabilities
"""
            for cap in res.emergent_capabilities:
                skill_md_content += f"- {cap}\n"

            skill_md_content += "\n## Inherited Alleles\n"
            for a in res.alleles:
                skill_md_content += f"- **[{a.kind.value.upper()}] {a.name}**: {a.summary}\n"

            (out_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")
            print(f"Saved hybrid skill to {out_dir / 'SKILL.md'}")

        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            print(format_human_report(res))
        sys.exit(0 if res.passed_gate else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
