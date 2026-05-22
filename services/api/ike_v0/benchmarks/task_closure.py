"""
IKE v0.1 Task Closure Helper

Produces bounded task closure objects after a study task completes.

Required shapes:
1. StudyResult:
   - result_id
   - trigger_packet_ref
   - inspected_artifacts
   - findings
   - claim_validations
   - blockers_encountered
   - confidence_delta
   - time_spent
   - completion_status
   - raw_notes

2. DecisionHandoff:
   - decision_id
   - study_result_ref
   - decision_type (continue_study|prototype|defer|reject)
   - justification
   - updated_claims
   - next_packet
   - rejection_reason
   - escalation_target
   - confidence
   - limitations

Current harness expectation:
- closure path supports: continue_study, prototype, defer, reject

This is a pure, benchmark-local helper: no LLM calls, no external API calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime, timezone

from .b2_trigger_packet import B2TriggerPacket
from .b3_deepening import B3ConceptDeepening


@dataclass
class StudyResult:
    """
    Structured study result for task closure.

    Fields:
    - result_id: Unique identifier for the result
    - trigger_packet_ref: Reference to the trigger packet this study addresses
    - inspected_artifacts: List of artifacts actually inspected
    - findings: Key findings from the study
    - claim_validations: Validation status of original claims
    - blockers_encountered: Blockers encountered during study
    - confidence_delta: Change in confidence (+/- from baseline)
    - time_spent: Actual time spent on the study
    - completion_status: completed|partial|abandoned
    - raw_notes: Raw notes from the study
    """
    result_id: str
    trigger_packet_ref: str
    inspected_artifacts: List[str]
    findings: List[str]
    claim_validations: List[Dict[str, str]]
    blockers_encountered: List[str]
    confidence_delta: float  # -1.0 to +1.0
    time_spent: str
    completion_status: str  # completed|partial|abandoned
    raw_notes: str
    concept: str = "harness"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "result_id": self.result_id,
            "trigger_packet_ref": self.trigger_packet_ref,
            "inspected_artifacts": self.inspected_artifacts,
            "findings": self.findings,
            "claim_validations": self.claim_validations,
            "blockers_encountered": self.blockers_encountered,
            "confidence_delta": self.confidence_delta,
            "time_spent": self.time_spent,
            "completion_status": self.completion_status,
            "raw_notes": self.raw_notes,
            "concept": self.concept,
            "created_at": self.created_at,
        }


@dataclass
class DecisionHandoff:
    """
    Structured decision handoff following study result.

    Fields:
    - decision_id: Unique identifier for the decision
    - study_result_ref: Reference to the study result this decision is based on
    - decision_type: One of continue_study|prototype|defer|reject
    - justification: Rationale for the decision
    - updated_claims: Updated claims based on study findings
    - next_packet: Reference to next trigger packet if applicable
    - rejection_reason: Reason if decision is reject
    - escalation_target: Target for escalation if applicable
    - confidence: Confidence in this decision (0.0 to 1.0)
    - limitations: Known limitations of this decision
    """
    decision_id: str
    study_result_ref: str
    decision_type: str  # continue_study|prototype|defer|reject
    justification: str
    updated_claims: List[str]
    next_packet: Optional[str]
    rejection_reason: Optional[str]
    escalation_target: Optional[str]
    confidence: float  # 0.0 to 1.0
    limitations: List[str]
    concept: str = "harness"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "decision_id": self.decision_id,
            "study_result_ref": self.study_result_ref,
            "decision_type": self.decision_type,
            "justification": self.justification,
            "updated_claims": self.updated_claims,
            "next_packet": self.next_packet,
            "rejection_reason": self.rejection_reason,
            "escalation_target": self.escalation_target,
            "confidence": self.confidence,
            "limitations": self.limitations,
            "concept": self.concept,
            "created_at": self.created_at,
        }


@dataclass
class TaskClosure:
    """
    Complete task closure combining study result and decision handoff.
    """
    study_result: StudyResult
    decision_handoff: DecisionHandoff
    closure_summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "study_result": self.study_result.to_dict(),
            "decision_handoff": self.decision_handoff.to_dict(),
            "closure_summary": self.closure_summary,
        }


def generate_study_result(
    trigger_packet: B2TriggerPacket,
    concept_deepening: Optional[B3ConceptDeepening] = None,
    inspected_repos: Optional[List[str]] = None,
    findings: Optional[List[str]] = None,
    claim_validations: Optional[List[Dict[str, str]]] = None,
    blockers_encountered: Optional[List[str]] = None,
    confidence_delta: float = 0.0,
    time_spent: str = "4-6 hours",
    completion_status: str = "completed",
    raw_notes: str = "",
    concept: str = "harness",
) -> StudyResult:
    """
    Generate a study result from completed study task.

    Args:
        trigger_packet: The B2-S4 trigger packet that initiated the study
        concept_deepening: Optional B3 concept deepening for claim validation
        inspected_repos: List of repositories actually inspected (required)
        findings: Key findings from the study (required)
        claim_validations: Validation status of claims (required)
        blockers_encountered: Blockers encountered during study (optional)
        confidence_delta: Change in confidence (default: 0.0)
        time_spent: Actual time spent (default: "4-6 hours")
        completion_status: completed|partial|abandoned (default: completed)
        raw_notes: Raw notes from the study (required)
        concept: The concept being studied (default: harness)

    Returns:
        StudyResult with findings, claim validations, confidence delta

    This is a pure helper: no LLM calls, no external API calls.
    Note: This helper records study results - it does not invent findings.
    Explicit findings, claim_validations, and raw_notes are required.
    """
    # Generate result ID
    result_id = _generate_result_id(trigger_packet.packet_id, concept)

    # Build inspected artifacts list
    inspected_artifacts = _build_inspected_artifacts(inspected_repos, trigger_packet)

    # Findings are required - do not generate defaults
    if findings is None:
        findings = []

    # Claim validations are required - do not generate defaults
    if claim_validations is None:
        claim_validations = []

    # Use provided blockers or empty list
    if blockers_encountered is None:
        blockers_encountered = []

    # Use provided raw notes - do not generate placeholder
    if not raw_notes:
        raw_notes = "No notes provided."

    return StudyResult(
        result_id=result_id,
        trigger_packet_ref=trigger_packet.packet_id,
        inspected_artifacts=inspected_artifacts,
        findings=findings,
        claim_validations=claim_validations,
        blockers_encountered=blockers_encountered,
        confidence_delta=confidence_delta,
        time_spent=time_spent,
        completion_status=completion_status,
        raw_notes=raw_notes,
        concept=concept,
    )


def generate_decision_handoff(
    study_result: StudyResult,
    decision_type: str,
    justification: str,
    confidence: float = 0.5,
    concept: str = "harness",
) -> DecisionHandoff:
    """
    Generate a decision handoff from study result.

    Args:
        study_result: The study result this decision is based on
        decision_type: One of continue_study|prototype|defer|reject (required)
        justification: Rationale for the decision (required)
        confidence: Confidence in this decision (default: 0.5)
        concept: The concept being evaluated (default: harness)

    Returns:
        DecisionHandoff with decision type, justification, next steps

    This is a pure helper: no LLM calls, no external API calls.
    Note: This helper records decisions - it does not auto-determine them.
    Explicit decision_type and justification are required.
    """
    # Generate decision ID
    decision_id = _generate_decision_id(study_result.result_id, concept)

    # Validate decision_type
    if decision_type not in ("continue_study", "prototype", "defer", "reject"):
        decision_type = "defer"  # Safe default

    # Determine next packet reference based on decision type
    next_packet = _determine_next_packet(decision_type, concept)

    # Determine rejection reason if applicable
    rejection_reason = None
    if decision_type == "reject":
        rejection_reason = "Decision: reject (see justification)"

    # No hardcoded escalation targets - set to None
    escalation_target = None

    # Build limitations based on decision type
    limitations = _build_decision_limitations(decision_type)

    # Updated claims - empty by default, caller can extend
    updated_claims = []

    return DecisionHandoff(
        decision_id=decision_id,
        study_result_ref=study_result.result_id,
        decision_type=decision_type,
        justification=justification,
        updated_claims=updated_claims,
        next_packet=next_packet,
        rejection_reason=rejection_reason,
        escalation_target=escalation_target,
        confidence=confidence,
        limitations=limitations,
        concept=concept,
    )


def generate_task_closure(
    trigger_packet: B2TriggerPacket,
    inspected_repos: List[str],
    findings: List[str],
    claim_validations: List[Dict[str, str]],
    raw_notes: str,
    decision_type: str,
    decision_justification: str,
    blockers_encountered: Optional[List[str]] = None,
    confidence_delta: float = 0.0,
    time_spent: str = "4-6 hours",
    completion_status: str = "completed",
    decision_confidence: float = 0.5,
    concept: str = "harness",
) -> TaskClosure:
    """
    Generate complete task closure from study result and decision handoff.

    Args:
        trigger_packet: The B2-S4 trigger packet that initiated the study
        inspected_repos: List of repositories actually inspected (required)
        findings: Key findings from the study (required)
        claim_validations: Validation status of claims (required)
        raw_notes: Raw notes from the study (required)
        decision_type: One of continue_study|prototype|defer|reject (required)
        decision_justification: Rationale for the decision (required)
        blockers_encountered: Blockers encountered (optional)
        confidence_delta: Change in confidence (default: 0.0)
        time_spent: Actual time spent (default: "4-6 hours")
        completion_status: completed|partial|abandoned (default: completed)
        decision_confidence: Confidence in decision (default: 0.5)
        concept: The concept being evaluated (default: harness)

    Returns:
        TaskClosure combining study result and decision handoff
    """
    # Generate study result with explicit inputs
    study_result = generate_study_result(
        trigger_packet=trigger_packet,
        inspected_repos=inspected_repos,
        findings=findings,
        claim_validations=claim_validations,
        blockers_encountered=blockers_encountered,
        confidence_delta=confidence_delta,
        time_spent=time_spent,
        completion_status=completion_status,
        raw_notes=raw_notes,
        concept=concept,
    )

    # Generate decision handoff with explicit inputs
    decision_handoff = generate_decision_handoff(
        study_result=study_result,
        decision_type=decision_type,
        justification=decision_justification,
        confidence=decision_confidence,
        concept=concept,
    )

    # Build closure summary
    closure_summary = _build_closure_summary(study_result, decision_handoff, concept)

    return TaskClosure(
        study_result=study_result,
        decision_handoff=decision_handoff,
        closure_summary=closure_summary,
    )


def _generate_result_id(packet_id: str, concept: str) -> str:
    """Generate unique result ID from trigger packet ID."""
    content = f"{packet_id}-{concept}-study-result"
    hash_suffix = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"SR-{concept.upper()[:6]}-{hash_suffix}"


def _generate_decision_id(result_id: str, concept: str) -> str:
    """Generate unique decision ID from study result ID."""
    content = f"{result_id}-{concept}-decision"
    hash_suffix = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"DH-{concept.upper()[:6]}-{hash_suffix}"


def _build_inspected_artifacts(
    inspected_repos: Optional[List[str]],
    trigger_packet: B2TriggerPacket,
) -> List[str]:
    """Build list of inspected artifacts."""
    artifacts = []

    if inspected_repos:
        for repo in inspected_repos[:3]:  # Limit to 3
            artifacts.append(f"Repository: {repo}")
    else:
        # Default artifacts based on trigger packet
        artifacts.append(f"Trigger packet: {trigger_packet.packet_id}")
        artifacts.append("Documentation review")
        artifacts.append("Pattern analysis")

    return artifacts


def _generate_default_findings(
    trigger_packet: B2TriggerPacket,
    concept_deepening: Optional[B3ConceptDeepening],
    concept: str,
) -> List[str]:
    """Generate default findings based on available context."""
    findings = [
        f"Evaluated {concept} patterns against project requirements",
        "Assessed integration complexity and effort",
        "Reviewed documentation quality and completeness",
    ]

    # Add findings from concept deepening if available
    if concept_deepening:
        if concept_deepening.boundary_positive:
            findings.append(f"Confirmed concept boundaries: {len(concept_deepening.boundary_positive)} positive indicators")
        if concept_deepening.mechanism_to_gap_mapping:
            findings.append(f"Validated {len(concept_deepening.mechanism_to_gap_mapping)} gap-addressing mechanisms")

    return findings


def _build_claim_validations(
    concept_deepening: Optional[B3ConceptDeepening],
    findings: List[str],
) -> List[Dict[str, str]]:
    """Build claim validations based on concept deepening and findings."""
    validations = []

    if concept_deepening:
        # Validate working definition
        validations.append({
            "claim": "Concept has testable working definition",
            "status": "validated" if concept_deepening.working_definition else "not_validated",
            "evidence": "B3 working definition present",
        })

        # Validate applicability
        validations.append({
            "claim": f"Concept is applicable to project",
            "status": "validated" if concept_deepening.applicability_judgment in ("partially_applicable", "directly_applicable") else "not_validated",
            "evidence": f"B3 judgment: {concept_deepening.applicability_judgment}",
        })

        # Validate target layer
        validations.append({
            "claim": "Target IKE layer identified",
            "status": "validated" if concept_deepening.target_ike_layer else "not_validated",
            "evidence": f"Target layer: {concept_deepening.target_ike_layer}",
        })
    else:
        # Default validations based on findings
        validations.append({
            "claim": "Study completed with findings",
            "status": "validated" if findings else "not_validated",
            "evidence": f"{len(findings)} findings documented",
        })

    return validations


def _determine_blockers(
    completion_status: str,
    trigger_packet: B2TriggerPacket,
) -> List[str]:
    """Determine blockers encountered during study."""
    blockers = []

    if completion_status == "abandoned":
        blockers.extend(trigger_packet.no_go_conditions[:2])
    elif completion_status == "partial":
        blockers.append("Time constraints limited full inspection")
        blockers.append("Some artifacts were inaccessible or incomplete")

    return blockers


def _calculate_confidence_delta(
    findings: List[str],
    claim_validations: List[Dict[str, str]],
    completion_status: str,
) -> float:
    """Calculate confidence delta based on study outcomes."""
    # Base delta on completion status
    if completion_status == "completed":
        base_delta = 0.2
    elif completion_status == "partial":
        base_delta = 0.1
    else:  # abandoned
        base_delta = -0.1

    # Adjust based on validated claims
    validated_count = sum(1 for v in claim_validations if v.get("status") == "validated")
    total_claims = len(claim_validations) if claim_validations else 1
    validation_bonus = (validated_count / total_claims) * 0.1

    # Adjust based on findings
    findings_bonus = min(len(findings) / 10.0, 0.1)  # Cap at 0.1

    delta = base_delta + validation_bonus + findings_bonus
    return round(max(-0.5, min(0.5, delta)), 2)  # Clamp to [-0.5, 0.5]


def _determine_decision_type(
    study_result: StudyResult,
    concept_deepening: Optional[B3ConceptDeepening],
) -> str:
    """Determine decision type based on study result."""
    # Check completion status first
    if study_result.completion_status == "abandoned":
        return "defer"

    # Check confidence delta
    if study_result.confidence_delta > 0.2:
        # Strong positive delta -> prototype
        return "prototype"
    elif study_result.confidence_delta > 0.0:
        # Moderate positive delta -> continue study or prototype based on findings
        if len(study_result.findings) >= 4:
            return "prototype"
        else:
            return "continue_study"
    elif study_result.confidence_delta < 0.0:
        # Negative delta -> reject or defer
        if len(study_result.blockers_encountered) >= 2:
            return "reject"
        else:
            return "defer"
    else:
        # Neutral delta -> continue study
        return "continue_study"


def _build_justification(
    study_result: StudyResult,
    decision_type: str,
    concept: str,
) -> str:
    """Build justification for the decision."""
    if decision_type == "prototype":
        return (
            f"Study results support advancing {concept} to prototype phase. "
            f"Confidence delta: +{study_result.confidence_delta}. "
            f"Validated {sum(1 for v in study_result.claim_validations if v.get('status') == 'validated')} claims. "
            f"Findings indicate direct applicability to project needs."
        )
    elif decision_type == "continue_study":
        return (
            f"Study results suggest further investigation of {concept} is warranted. "
            f"Confidence delta: {study_result.confidence_delta:+.2f}. "
            f"Additional repository inspection or deeper technical analysis recommended."
        )
    elif decision_type == "defer":
        return (
            f"Study of {concept} deferred pending resolution of blockers. "
            f"Confidence delta: {study_result.confidence_delta:+.2f}. "
            f"Blockers encountered: {len(study_result.blockers_encountered)}. "
            f"Revisit when conditions improve."
        )
    elif decision_type == "reject":
        return (
            f"Study results indicate {concept} is not suitable for adoption. "
            f"Confidence delta: {study_result.confidence_delta:+.2f}. "
            f"Significant blockers or misalignment with project needs identified."
        )
    else:
        return f"Decision based on study results for {concept}."


def _build_updated_claims(
    study_result: StudyResult,
    decision_type: str,
    concept: str,
) -> List[str]:
    """Build updated claims based on study findings."""
    claims = []

    if decision_type in ("prototype", "continue_study"):
        claims.append(f"{concept} shows promise for project integration")
        claims.append("Further investment justified based on study findings")
    elif decision_type == "defer":
        claims.append(f"{concept} evaluation paused pending blocker resolution")
        claims.append("Core value proposition remains unvalidated")
    elif decision_type == "reject":
        claims.append(f"{concept} not suitable for current project needs")
        claims.append("Alternative approaches should be explored")

    return claims


def _determine_next_packet(
    decision_type: str,
    concept: str,
) -> Optional[str]:
    """Determine next packet reference based on decision."""
    if decision_type == "prototype":
        return f"B2-S4-{concept.upper()[:8]}-PROTOTYPE-PENDING"
    elif decision_type == "continue_study":
        return f"B2-S4-{concept.upper()[:8]}-STUDY2-PENDING"
    else:
        return None


def _determine_rejection_reason(
    decision_type: str,
    study_result: StudyResult,
) -> Optional[str]:
    """Determine rejection reason if decision is reject."""
    if decision_type == "reject":
        if study_result.blockers_encountered:
            return f"Blockers: {', '.join(study_result.blockers_encountered[:2])}"
        else:
            return "Concept misalignment with project requirements"
    return None


def _determine_escalation_target(
    decision_type: str,
) -> Optional[str]:
    """Determine escalation target if applicable."""
    if decision_type == "reject":
        return "Architecture review board"
    elif decision_type == "prototype":
        return "Development team lead"
    return None


def _calculate_decision_confidence(
    study_result: StudyResult,
    decision_type: str,
) -> float:
    """Calculate confidence in the decision."""
    # Base confidence on completion status
    if study_result.completion_status == "completed":
        base_conf = 0.7
    elif study_result.completion_status == "partial":
        base_conf = 0.5
    else:
        base_conf = 0.3

    # Adjust based on confidence delta
    delta_factor = max(0, study_result.confidence_delta)
    conf = base_conf + (delta_factor * 0.2)

    # Adjust based on decision type
    if decision_type == "reject" and len(study_result.blockers_encountered) >= 2:
        conf += 0.1  # More confident in rejection with multiple blockers

    return round(min(0.95, conf), 2)


def _build_decision_limitations(
    decision_type: str,
) -> List[str]:
    """Build limitations for the decision."""
    limitations = [
        "Decision based on bounded study scope",
        "May not capture all integration complexities",
    ]

    if decision_type in ("prototype", "continue_study"):
        limitations.append("Prototype may reveal additional challenges")
    elif decision_type == "reject":
        limitations.append("Future re-evaluation may be warranted as project evolves")
    elif decision_type == "defer":
        limitations.append("Deferred decision should be revisited within 3 months")

    return limitations


def _build_closure_summary(
    study_result: StudyResult,
    decision_handoff: DecisionHandoff,
    concept: str,
) -> str:
    """Build summary of task closure."""
    return (
        f"Task closure for {concept}: Study {study_result.completion_status} "
        f"with confidence delta {study_result.confidence_delta:+.2f}. "
        f"Decision: {decision_handoff.decision_type.replace('_', ' ')}. "
        f"Next steps: {decision_handoff.justification[:100]}..."
    )
