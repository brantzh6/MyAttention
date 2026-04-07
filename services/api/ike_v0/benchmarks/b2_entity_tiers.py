"""
IKE v0.1 B2 Entity Tier Classifier

Classifies ranked entities from B1 trend bundles into three tiers:
- concept_defining: entities that define, originate, or fundamentally shape the concept
- ecosystem_relevant: entities that shape the surrounding ecosystem, adoption patterns, or discourse
- implementation_relevant: entities directly relevant to implementing or applying the concept in this project

This is benchmark-local: uses only the B1 trend bundle, no LLM calls, no external API calls.

B4 Integration:
- Accepts optional B4 evidence layer tags as tiebreak/classification signal
- Media/context evidence cannot boost entities to concept_defining tier
- Stronger evidence layers (authoritative_official, expert_maintainer) improve tier confidence
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .b1_harness import HarnessTrendBundle, RankedEntity
from .b4_evidence_layers import tag_ranked_entities, B4EvidenceLayers, EVIDENCE_LAYER_PRIORITY


@dataclass
class TierEntry:
    """A single entry in an entity tier."""

    entity_name: str
    entity_type: str
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "rationale": self.rationale,
        }


@dataclass
class EntityTier:
    """A tier containing classified entities."""

    tier_name: str
    description: str
    entries: List[TierEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tier_name": self.tier_name,
            "description": self.description,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class B2EntityTiers:
    """Structured output object for B2 entity tiers."""

    concept_defining: EntityTier
    ecosystem_relevant: EntityTier
    implementation_relevant: EntityTier
    topic: str = "harness"
    benchmark_id: str = "B2-S1"
    notes: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "concept_defining": self.concept_defining.to_dict(),
            "ecosystem_relevant": self.ecosystem_relevant.to_dict(),
            "implementation_relevant": self.implementation_relevant.to_dict(),
            "topic": self.topic,
            "benchmark_id": self.benchmark_id,
            "notes": self.notes,
            "limitations": self.limitations,
        }


def classify_benchmark_entity_tiers(
    bundle: HarnessTrendBundle,
    concept: str = "harness",
    evidence_layers: Optional[B4EvidenceLayers] = None,
) -> B2EntityTiers:
    """
    Classify ranked entities from a B1 trend bundle into three tiers.

    Args:
        bundle: The B1 HarnessTrendBundle containing ranked entities
        concept: The concept being classified (default: "harness")
        evidence_layers: Optional B4 evidence layer tags for tiebreaking

    Returns:
        B2EntityTiers object with entities classified into three tiers

    Tier semantics:
        - concept_defining: entities that define, originate, or fundamentally shape the concept
        - ecosystem_relevant: entities that shape the surrounding ecosystem, adoption patterns, or discourse
        - implementation_relevant: entities directly relevant to implementing or applying the concept

    B4 Integration:
        - If evidence_layers provided, uses evidence layer as tiebreak signal
        - Media/context evidence cannot boost entities to concept_defining tier
        - Stronger evidence layers improve rationale specificity

    This is a pure helper: no LLM calls, no external API calls, evidence-grounded and bounded.
    """
    # Derive evidence layers if not provided
    if evidence_layers is None:
        evidence_layers = tag_ranked_entities(bundle.ranked_entities, topic=concept)

    # Build a lookup map for evidence layers by entity name
    evidence_map = {
        tag.entity_name: tag.evidence_layer
        for tag in evidence_layers.tagged_entities
    }

    # Initialize tiers with descriptions
    concept_defining_tier = EntityTier(
        tier_name="concept_defining",
        description=f"Entities that define, originate, or fundamentally shape the {concept} concept",
    )
    ecosystem_relevant_tier = EntityTier(
        tier_name="ecosystem_relevant",
        description=f"Entities that shape the surrounding ecosystem, adoption patterns, or discourse around {concept}",
    )
    implementation_relevant_tier = EntityTier(
        tier_name="implementation_relevant",
        description=f"Entities directly relevant to implementing or applying {concept} in this project",
    )

    # Classification patterns based on entity names and types
    # These are heuristic patterns grounded in the B1 benchmark evidence

    for entity in bundle.ranked_entities:
        name_lower = entity.name.lower()
        entity_type = entity.entity_type
        relevance = entity.relevance_reason.lower()
        evidence_layer = evidence_map.get(entity.name, None)

        # Determine tier based on evidence patterns
        tier_assignment = _classify_entity_to_tier(
            name=name_lower,
            entity_type=entity_type,
            relevance_reason=relevance,
            concept=concept,
            evidence_layer=evidence_layer,
        )

        rationale = _build_rationale(entity, tier_assignment, concept, evidence_layer)

        entry = TierEntry(
            entity_name=entity.name,
            entity_type=entity_type,
            rationale=rationale,
        )

        if tier_assignment == "concept_defining":
            concept_defining_tier.entries.append(entry)
        elif tier_assignment == "ecosystem_relevant":
            ecosystem_relevant_tier.entries.append(entry)
        else:
            implementation_relevant_tier.entries.append(entry)

    # Build notes and limitations
    notes = (
        f"B2 entity tier classification for concept '{concept}'. "
        f"Classification is heuristic and evidence-grounded, using B1 trend bundle data"
    )
    if evidence_layers:
        notes += f" and B4 evidence layers. "
    else:
        notes += ". "
    notes += f"Total entities classified: {len(bundle.ranked_entities)}. "

    limitations = [
        "Classification is heuristic, not LLM-based",
        "Limited to B1 trend bundle evidence only",
        "May misclassify entities with ambiguous roles",
        "Does not capture temporal evolution of entity roles",
        "Media/context evidence cannot boost to concept_defining tier",
    ]

    return B2EntityTiers(
        concept_defining=concept_defining_tier,
        ecosystem_relevant=ecosystem_relevant_tier,
        implementation_relevant=implementation_relevant_tier,
        topic=concept,
        benchmark_id="B2-S1",
        notes=notes,
        limitations=limitations,
    )


def _classify_entity_to_tier(
    name: str,
    entity_type: str,
    relevance_reason: str,
    concept: str = "harness",
    evidence_layer: Optional[str] = None,
) -> str:
    """
    Classify a single entity to a tier based on heuristic patterns.

    Args:
        name: Entity name (lowercase)
        entity_type: Entity type (person, repository, organization, etc.)
        relevance_reason: Relevance reason from B1 ranking
        concept: The concept being classified
        evidence_layer: Optional B4 evidence layer for tiebreaking

    Returns one of: "concept_defining", "ecosystem_relevant", "implementation_relevant"

    B4 Integration:
        - Media/context evidence cannot boost to concept_defining tier
        - authoritative_official or expert_maintainer layers boost concept_defining score
        - implementation_repository layer boosts implementation_relevant score
    """
    # Concept-defining patterns:
    # - Primary authors/creators of the core concept
    # - Original repositories or foundational projects
    # - Entities mentioned as defining/originating the concept

    concept_defining_signals = [
        "author", "creator", "originator", "founder", "maintainer", "core",
        "primary", "main", "foundational", "defining", "seminal",
    ]

    # Ecosystem-relevant patterns:
    # - Organizations, communities, research groups
    # - Entities shaping adoption or discourse
    # - Secondary contributors, adopters, evangelists

    ecosystem_relevant_signals = [
        "organization", "community", "research", "lab", "institute",
        "adoption", "discourse", "ecosystem", "network", "group",
        "contributor", "advocate", "evangelist", "partner",
    ]

    # Implementation-relevant patterns:
    # - Tools, frameworks, utilities
    # - Entities directly useful for building/implementing
    # - Practical applications, integrations
    # - Evaluation/benchmark/audit workflows

    implementation_relevant_signals = [
        "tool", "framework", "utility", "library", "package", "sdk",
        "implementation", "application", "integration", "practice",
        "guide", "tutorial", "example", "template", "boilerplate",
        "evaluation", "benchmark", "validation", "audit", "verification",
    ]

    # Distribution/catalog patterns (should NOT be implementation_relevant):
    # - Skill catalogs, indexes, distribution surfaces
    # - Installation/discovery repositories
    # - clawhub-style skill registries
    # These belong in ecosystem_relevant, not implementation_relevant

    distribution_catalog_signals = [
        "catalog", "index", "skills", "skill", "clawhub", "install",
        "distribution", "registry", "registry", "marketplace", "discover",
        "master-skills", "skill-pack", "skill-index",
    ]

    # Score the entity against each tier
    concept_score = sum(1 for signal in concept_defining_signals if signal in name or signal in relevance_reason)
    ecosystem_score = sum(1 for signal in ecosystem_relevant_signals if signal in name or signal in relevance_reason)
    implementation_score = sum(1 for signal in implementation_relevant_signals if signal in name or signal in relevance_reason)

    # Check for distribution/catalog signals - these should NOT count as implementation_relevant
    is_distribution_catalog = any(signal in name for signal in distribution_catalog_signals)

    # Entity type priors (based on typical roles)
    type_priors = {
        "person": {"concept_defining": 0.3, "ecosystem_relevant": 0.4, "implementation_relevant": 0.3},
        "repository": {"concept_defining": 0.4, "ecosystem_relevant": 0.2, "implementation_relevant": 0.4},
        "organization": {"concept_defining": 0.2, "ecosystem_relevant": 0.6, "implementation_relevant": 0.2},
        "community": {"concept_defining": 0.1, "ecosystem_relevant": 0.7, "implementation_relevant": 0.2},
    }

    prior = type_priors.get(entity_type, {"concept_defining": 0.2, "ecosystem_relevant": 0.4, "implementation_relevant": 0.4})

    # Apply priors as tiebreakers
    concept_score += prior["concept_defining"]
    ecosystem_score += prior["ecosystem_relevant"]
    implementation_score += prior["implementation_relevant"]

    # CRITICAL: Distribution/catalog repositories should NOT be implementation_relevant
    # They belong in ecosystem_relevant (distribution/discovery surface)
    if is_distribution_catalog:
        # Reduce implementation score significantly
        implementation_score *= 0.3
        # Boost ecosystem score (it's a distribution surface)
        ecosystem_score += 0.5

    # B4 evidence layer integration
    if evidence_layer:
        # Strong evidence layers boost concept_defining (official/maintainer authority)
        if evidence_layer == "authoritative_official":
            concept_score += 0.5  # Strong boost for official sources
        elif evidence_layer == "expert_maintainer":
            concept_score += 0.3  # Moderate boost for experts/maintainers
        elif evidence_layer == "implementation_repository":
            implementation_score += 0.3  # Boost for implementation repos
        elif evidence_layer == "community_discourse":
            ecosystem_score += 0.2  # Mild boost for community
        # CRITICAL: media_context cannot boost concept_defining
        # It only gets a small ecosystem boost at most
        elif evidence_layer == "media_context":
            ecosystem_score += 0.1  # Minimal boost, cannot reach concept_defining

    # Assign to highest-scoring tier
    scores = {
        "concept_defining": concept_score,
        "ecosystem_relevant": ecosystem_score,
        "implementation_relevant": implementation_score,
    }

    return max(scores, key=scores.get)


def _build_rationale(
    entity: RankedEntity,
    tier: str,
    concept: str,
    evidence_layer: Optional[str] = None,
) -> str:
    """Build a human-readable rationale for the tier assignment."""
    # Build evidence layer context if available
    evidence_context = ""
    if evidence_layer:
        evidence_context = f" (evidence: {evidence_layer.replace('_', ' ')})"

    tier_reasons = {
        "concept_defining": (
            f"Classified as concept-defining for {concept}: entity shows signals of being a primary "
            f"author, creator, or foundational contributor based on relevance pattern '{entity.relevance_reason}'"
            f"{evidence_context}"
        ),
        "ecosystem_relevant": (
            f"Classified as ecosystem-relevant for {concept}: entity shapes the surrounding ecosystem, "
            f"adoption, or discourse based on relevance pattern '{entity.relevance_reason}'"
            f"{evidence_context}"
        ),
        "implementation_relevant": (
            f"Classified as implementation-relevant for {concept}: entity is directly useful for "
            f"implementing or applying the concept based on relevance pattern '{entity.relevance_reason}'"
            f"{evidence_context}"
        ),
    }

    return tier_reasons.get(tier, f"Classified based on evidence: {entity.relevance_reason}")
