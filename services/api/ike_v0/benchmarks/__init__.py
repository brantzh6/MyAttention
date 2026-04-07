"""
IKE v0.1 Benchmarks

Real-world benchmark helpers for IKE validation.
"""

from .b1_discovery_client import (
    B1_HARNESS_CONTEXT_TOPICS,
    DiscoveryClientError,
    DiscoveryResponseError,
    _build_b1_discovery_topic,
    _infer_entity_type,
    call_source_discovery,
    run_harness_benchmark,
)
from .b1_harness import (
    detect_harness_trend_bundle,
    rank_harness_entities,
    reshape_discovery_to_benchmark_entities,
)
from .b1_knowledge import (
    KnowledgeSummary,
    generate_harness_knowledge_summary,
)
from .b1_evolution import (
    EvolutionJudgment,
    generate_evolution_judgment,
    MAINLINE_GAPS,
)
from .b2_entity_tiers import (
    B2EntityTiers,
    EntityTier,
    TierEntry,
    classify_benchmark_entity_tiers,
)
from .b2_gap_mapping import (
    B2GapMappingResult,
    GapMapping,
    map_concept_to_mainline_gaps,
)
from .b2_recommendation import (
    B2Recommendation,
    generate_research_recommendation,
)
from .b2_trigger_packet import (
    B2TriggerPacket,
    generate_trigger_packet,
)
from .b3_deepening import (
    B3ConceptDeepening,
    generate_concept_deepening,
)
from .b4_evidence_layers import (
    B4EvidenceLayers,
    EvidenceLayerTag,
    EVIDENCE_LAYER_PRIORITY,
    VALID_EVIDENCE_LAYERS,
    tag_evidence_layer,
    tag_benchmark_evidence_layers,
    tag_ranked_entities,
)
from .b4_report import (
    B4BenchmarkReport,
    compose_b4_benchmark_report,
    get_evidence_layer_priority_order,
    summarize_evidence_quality,
)
from .task_closure import (
    StudyResult,
    DecisionHandoff,
    TaskClosure,
    generate_study_result,
    generate_decision_handoff,
    generate_task_closure,
)

__all__ = [
    "B1_HARNESS_CONTEXT_TOPICS",
    "B2EntityTiers",
    "B2GapMappingResult",
    "B2Recommendation",
    "B2TriggerPacket",
    "B3ConceptDeepening",
    "B4BenchmarkReport",
    "B4EvidenceLayers",
    "DecisionHandoff",
    "DiscoveryClientError",
    "DiscoveryResponseError",
    "EVIDENCE_LAYER_PRIORITY",
    "EntityTier",
    "EvidenceLayerTag",
    "EvolutionJudgment",
    "GapMapping",
    "KnowledgeSummary",
    "MAINLINE_GAPS",
    "StudyResult",
    "TaskClosure",
    "TierEntry",
    "VALID_EVIDENCE_LAYERS",
    "_build_b1_discovery_topic",
    "_infer_entity_type",
    "call_source_discovery",
    "classify_benchmark_entity_tiers",
    "compose_b4_benchmark_report",
    "decision_handoff",
    "detect_harness_trend_bundle",
    "generate_concept_deepening",
    "generate_decision_handoff",
    "generate_evolution_judgment",
    "generate_harness_knowledge_summary",
    "generate_research_recommendation",
    "generate_study_result",
    "generate_task_closure",
    "generate_trigger_packet",
    "get_evidence_layer_priority_order",
    "map_concept_to_mainline_gaps",
    "rank_harness_entities",
    "reshape_discovery_to_benchmark_entities",
    "run_harness_benchmark",
    "summarize_evidence_quality",
    "tag_benchmark_evidence_layers",
    "tag_evidence_layer",
    "tag_ranked_entities",
]
