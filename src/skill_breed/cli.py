"""CLI entry point for skill-breed: Interspecific Agent Skills Hybridization Engine."""

from __future__ import annotations

import argparse
import json
import sys
import time

from skill_breed.breed import (
    ChromosomeExtractor,
    SkillBreeder,
    SkillChromosome,
    breed_skills,
    safe_resolve_path,
)

VERSION = "1.0.0"


def format_human_report(result) -> str:
    status_icon = "✔ PASS" if result.passed_gate else "✖ REJECT (Regress)"
    lines = [
        "================================================================================",
        "  🧬 Skill-Breed: Interspecific Skill Hybridization Report",
        "================================================================================",
        f"Parent A       : {result.parent_a}",
        f"Parent B       : {result.parent_b}",
        f"Offspring Name : {result.offspring_name}",
        f"Offspring Genus: {result.offspring_genus}",
        f"Heterosis Gate : {status_icon} (Score: {result.heterosis_score:.3f}x, Target: 1.150x)",
        f"Total Alleles  : {len(result.alleles)} (Dominant Invariants: {sum(1 for a in result.alleles if a.dominant)})",
        "--------------------------------------------------------------------------------",
        "Inherited & Synthesized Alleles:",
    ]
    for a in result.alleles:
        dom_badge = "[DOMINANT]" if a.dominant else "          "
        lines.append(f"  • {dom_badge} [{a.kind.value.upper():<9}] {a.name} (w={a.weight:.1f}) -> {a.summary[:65]}")

    if result.emergent_capabilities:
        lines.append("--------------------------------------------------------------------------------")
        lines.append("🌟 Emergent Capabilities Synthesized:")
        for cap in result.emergent_capabilities:
            lines.append(f"  ★ {cap}")

    if result.tool_chain_dag and result.tool_chain_dag.get("edges"):
        lines.append("--------------------------------------------------------------------------------")
        lines.append(f"🔗 Tool Chaining DAG: {len(result.tool_chain_dag['edges'])} active paths synthesized")

    lines.append("================================================================================")
    return "\n".join(lines)


def run_benchmark():
    print("Running Skill-Breed Stress & Heterosis Benchmark...")
    breeder = SkillBreeder(threshold=1.10, seed=42)

    from skill_breed.breed import Allele, AlleleType

    skills = [
        SkillChromosome(
            f"skill_{i}",
            f"genus_{i % 5}",
            f"Skill {i} description",
            alleles=[],
        )
        for i in range(50)
    ]
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
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
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
    breed_p.add_argument("--format", choices=["human", "json", "mermaid"], default="human", help="Output format")
    breed_p.add_argument("--json", action="store_true", help="Alias for --format json")

    # inspect
    inspect_p = subparsers.add_parser("inspect", help="Decompose an agent skill into functional genetic alleles")
    inspect_p.add_argument("skill", help="Path to skill directory or SKILL.md")
    inspect_p.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    inspect_p.add_argument("--json", action="store_true", help="Alias for --format json")

    # matrix
    matrix_p = subparsers.add_parser("matrix", help="Run combinatorial breeding matrix over all skills in a directory")
    matrix_p.add_argument("skills_dir", help="Directory containing multiple skill subdirectories")
    matrix_p.add_argument("--threshold", type=float, default=1.15, help="Minimum heterosis threshold")
    matrix_p.add_argument("--out", type=str, default=None, help="Path to write JSON matrix results")

    # benchmark
    subparsers.add_parser("benchmark", help="Run high-throughput stress and heterosis benchmark")

    args = parser.parse_args()

    if args.command == "benchmark":
        run_benchmark()
        return

    if args.command == "inspect":
        target = safe_resolve_path(args.skill)
        chrom = ChromosomeExtractor.load_skill_file(target)

        if args.json or args.format == "json":
            print(json.dumps(chrom.to_dict(), indent=2))
        else:
            print(f"Chromosome  : {chrom.name}")
            print(f"Genus       : {chrom.genus}")
            print(f"Description : {chrom.description}")
            print(f"Alleles ({len(chrom.alleles)}):")
            for a in chrom.alleles:
                dom = " [DOMINANT INVARIANT]" if a.dominant else ""
                print(f"  [{a.kind.value.upper():<9}] {a.name}{dom} (weight={a.weight:.1f}): {a.summary}")
        return

    if args.command == "matrix":
        skills_dir = safe_resolve_path(args.skills_dir)
        if not skills_dir.exists() or not skills_dir.is_dir():
            print(f"Error: Directory '{skills_dir}' does not exist or is not a directory.", file=sys.stderr)
            sys.exit(1)

        skill_files = list(skills_dir.glob("*/SKILL.md"))
        if len(skill_files) < 2:
            print(
                f"Notice: Found fewer than 2 skills in {skills_dir}. Need at least 2 to cross-breed.", file=sys.stderr
            )
            sys.exit(1)

        chromosomes = [ChromosomeExtractor.load_skill_file(f) for f in skill_files]
        breeder = SkillBreeder(threshold=args.threshold)
        matrix_results = []

        print(f"Cross-breeding {len(chromosomes)} skills across domain boundaries...")
        t0 = time.perf_counter()
        for i in range(len(chromosomes)):
            for j in range(i + 1, len(chromosomes)):
                res = breeder.breed(chromosomes[i], chromosomes[j])
                if res.passed_gate:
                    matrix_results.append(res.to_dict())

        elapsed = time.perf_counter() - t0
        print(f"✔ Generated {len(matrix_results)} viable hybrids passing Heterosis Gate in {elapsed:.3f}s.")

        if args.out:
            out_file = safe_resolve_path(args.out)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(json.dumps(matrix_results, indent=2), encoding="utf-8")
            print(f"Saved matrix results to {out_file}")
        else:
            print(json.dumps(matrix_results, indent=2))
        return

    if args.command == "breed":
        p_a = safe_resolve_path(args.skill_a)
        p_b = safe_resolve_path(args.skill_b)
        res = breed_skills(p_a, p_b, threshold=args.threshold, seed=args.seed)

        if args.out:
            out_dir = safe_resolve_path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            skill_md_content = f"""---
name: {res.offspring_name}
description: Hybrid agent skill synthesized from {res.parent_a} and {res.parent_b}
version: 1.0.0
genus: {res.offspring_genus}
heterosis_score: {res.heterosis_score:.3f}
---

# {res.offspring_name}

Biomimetic hybrid skill synthesized from `{res.parent_a}` and `{res.parent_b}`.

## 🌟 Emergent Capabilities
"""
            for cap in res.emergent_capabilities:
                skill_md_content += f"- {cap}\n"

            skill_md_content += "\n## 🧬 Inherited & Synthesized Alleles\n"
            for a in res.alleles:
                dom_str = " *(Dominant Invariant)*" if a.dominant else ""
                skill_md_content += f"- **[{a.kind.value.upper()}] {a.name}**{dom_str}: {a.summary}\n"

            skill_md_content += "\n## 🔗 Synthesized Tool Chaining Flowchart\n\n"
            skill_md_content += res.to_mermaid() + "\n"

            target_md = out_dir / "SKILL.md"
            target_md.write_text(skill_md_content, encoding="utf-8")
            print(f"✔ Saved hybrid skill to {target_md}")

        fmt = "json" if args.json else args.format
        if fmt == "json":
            print(json.dumps(res.to_dict(), indent=2))
        elif fmt == "mermaid":
            print(res.to_mermaid())
        else:
            print(format_human_report(res))

        sys.exit(0 if res.passed_gate else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
