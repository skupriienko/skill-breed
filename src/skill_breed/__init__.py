"""skill-breed: Biomimetic Interspecific Cross-Breeding Engine for AI Agent Skills."""

from skill_breed.breed import (
    Allele,
    AlleleType,
    ChromosomeExtractor,
    HeterosisEvaluator,
    HybridMutationFuzzer,
    HybridResult,
    SkillBreeder,
    SkillChromosome,
    breed_skills,
)

__version__ = "1.0.0"
__all__ = [
    "Allele",
    "AlleleType",
    "ChromosomeExtractor",
    "HeterosisEvaluator",
    "HybridMutationFuzzer",
    "HybridResult",
    "SkillBreeder",
    "SkillChromosome",
    "breed_skills",
]
