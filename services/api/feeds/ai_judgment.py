"""
Internal AI judgment substrate for source discovery.

This module provides reusable judgment capabilities:
- provider-aware default model resolution
- JSON parsing with fence stripping and malformed fallback
- judgment normalization against allowed candidates
- verdict-overlap comparison for panel analysis
- disagreement / consensus insight derivation
"""

import json
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field

from config import get_effective_qwen_default_model, get_settings


# ── Constants ────────────────────────────────────────────────────────────────

_CONSENSUS_VERDICTS = {"follow", "ignore"}
_HIGH_CONFIDENCE_THRESHOLD = 0.75
_LOW_CONFIDENCE_THRESHOLD = 0.5


# ── Response models (shared between route and substrate) ─────────────────────

class SourceCandidateJudgment(BaseModel):
    object_key: str
    item_type: str
    verdict: str
    rationale: str
    confidence: float
    review_priority: str = "normal"


class SourceDiscoveryJudgePanelConsensusItem(BaseModel):
    object_key: str
    shared_verdict: str
    primary_confidence: float
    secondary_confidence: float
    primary_rationale: str
    secondary_rationale: str
    why_consensus: str


class SourceDiscoveryJudgePanelDisagreementItem(BaseModel):
    object_key: str
    primary_verdict: str
    secondary_verdict: str
    primary_confidence: float
    secondary_confidence: float
    primary_rationale: str
    secondary_rationale: str
    divergence_type: str
    why_opportunity: str


class SourceDiscoveryJudgePanelInsights(BaseModel):
    consensus_worthy: List[SourceDiscoveryJudgePanelConsensusItem] = []
    disagreement_worthy: List[SourceDiscoveryJudgePanelDisagreementItem] = []
    follow_up_hints: List[str] = []


class SourceJudgmentSelectiveAbsorptionItem(BaseModel):
    object_key: str
    proposed_action: str
    basis: str
    confidence: float
    explanation: str


class SourceJudgmentSelectiveAbsorptionAdvice(BaseModel):
    ready_to_follow: List[SourceJudgmentSelectiveAbsorptionItem] = []
    ready_to_suppress: List[SourceJudgmentSelectiveAbsorptionItem] = []
    needs_manual_review: List[SourceJudgmentSelectiveAbsorptionItem] = []
    watch_candidates: List[SourceJudgmentSelectiveAbsorptionItem] = []
    controller_notes: List[str] = []


# ── Provider-aware default model resolution ───────────────────────────────────

def default_model_for_provider(provider: str) -> str:
    """Resolve default model for a given LLM provider."""
    normalized = (provider or "").strip().lower()
    if normalized == "anthropic":
        return "claude-3-5-sonnet-20241022"
    if normalized == "openai":
        return "gpt-4o"
    if normalized == "ollama":
        return "qwen2:7b"
    return get_effective_qwen_default_model(get_settings())


# ── JSON parsing with fence stripping and malformed fallback ──────────────────

def parse_ai_judgment_payload(raw: str) -> Tuple[Dict[str, Any], str]:
    """Parse AI judgment JSON with fence stripping and malformed fallback."""
    cleaned = str(raw or "").strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload, "valid_json"
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    return {"summary": "", "judgments": []}, "invalid_json_fallback"


# ── Judgment normalization against allowed candidates ──────────────────────────

def normalize_ai_judgments(
    allowed_object_keys: set,
    payload: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], str, int]:
    """
    Normalize raw judgments against allowed candidates.

    Returns:
        (normalized_judgments, summary, discarded_count)
        Each normalized judgment dict contains: object_key, verdict, rationale, confidence, review_priority
    """
    allowed_verdicts = {"follow", "review", "ignore"}
    allowed_priorities = {"high", "normal", "low"}
    summary = str(payload.get("summary", "") or "").strip()
    judgments: List[Dict[str, Any]] = []
    raw_judgments = list(payload.get("judgments", []))
    for raw in raw_judgments:
        if not isinstance(raw, dict):
            continue
        object_key = str(raw.get("object_key", "")).strip()
        if object_key not in allowed_object_keys:
            continue
        verdict = str(raw.get("verdict", "")).strip().lower()
        if verdict not in allowed_verdicts:
            continue
        priority = str(raw.get("review_priority", "normal") or "normal").strip().lower()
        if priority not in allowed_priorities:
            priority = "normal"
        try:
            confidence = float(raw.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        judgments.append({
            "object_key": object_key,
            "verdict": verdict,
            "rationale": str(raw.get("rationale", "") or "").strip(),
            "confidence": max(0.0, min(1.0, confidence)),
            "review_priority": priority,
        })
    discarded_judgments = max(0, len(raw_judgments) - len(judgments))
    return judgments, summary, discarded_judgments


def normalize_ai_judgments_from_candidates(
    candidates: List[Any],
    payload: Dict[str, Any],
) -> Tuple[List[SourceCandidateJudgment], str, int]:
    """
    Normalize raw judgments against candidate objects with item_type.

    Args:
        candidates: List of candidate objects with object_key and item_type attributes
        payload: Raw AI judgment payload

    Returns:
        (normalized_judgments, summary, discarded_count)
    """
    allowed_keys = {candidate.object_key: candidate for candidate in candidates}
    raw_judgments, summary, discarded = normalize_ai_judgments(set(allowed_keys), payload)
    judgments: List[SourceCandidateJudgment] = []
    for j in raw_judgments:
        candidate = allowed_keys[j["object_key"]]
        judgments.append(
            SourceCandidateJudgment(
                object_key=j["object_key"],
                item_type=candidate.item_type,
                verdict=j["verdict"],
                rationale=j["rationale"],
                confidence=j["confidence"],
                review_priority=j["review_priority"],
            )
        )
    return judgments, summary, discarded


# ── Verdict-overlap comparison for panel analysis ─────────────────────────────

def compare_judgment_verdict_overlap(
    primary: List[SourceCandidateJudgment],
    secondary: List[SourceCandidateJudgment],
) -> Dict[str, Any]:
    """Compare verdict overlap between two judgment sets."""
    primary_map = {judgment.object_key: judgment.verdict for judgment in primary}
    secondary_map = {judgment.object_key: judgment.verdict for judgment in secondary}
    shared_keys = sorted(set(primary_map) & set(secondary_map))
    agreed = [key for key in shared_keys if primary_map[key] == secondary_map[key]]
    disagreed = [key for key in shared_keys if primary_map[key] != secondary_map[key]]
    primary_only = sorted(set(primary_map) - set(secondary_map))
    secondary_only = sorted(set(secondary_map) - set(primary_map))
    return {
        "shared_candidates": len(shared_keys),
        "agreement_count": len(agreed),
        "disagreement_count": len(disagreed),
        "primary_only_count": len(primary_only),
        "secondary_only_count": len(secondary_only),
        "agreed_object_keys": agreed,
        "disagreed_object_keys": disagreed,
        "panel_signal": (
            "stable"
            if shared_keys and not disagreed and not primary_only and not secondary_only
            else "mixed"
        ),
    }


# ── Disagreement / consensus insight derivation ────────────────────────────────

def derive_panel_insights(
    primary: List[SourceCandidateJudgment],
    secondary: List[SourceCandidateJudgment],
) -> SourceDiscoveryJudgePanelInsights:
    """Derive consensus and disagreement insights from panel judgments."""
    primary_map = {j.object_key: j for j in primary}
    secondary_map = {j.object_key: j for j in secondary}
    shared_keys = sorted(set(primary_map) & set(secondary_map))

    consensus_worthy: List[SourceDiscoveryJudgePanelConsensusItem] = []
    disagreement_worthy: List[SourceDiscoveryJudgePanelDisagreementItem] = []
    follow_up_hints: List[str] = []

    for key in shared_keys:
        pj = primary_map[key]
        sj = secondary_map[key]

        if pj.verdict == sj.verdict:
            # Both models agree — check if it is consensus-worthy
            avg_confidence = (pj.confidence + sj.confidence) / 2.0
            if pj.verdict in _CONSENSUS_VERDICTS and avg_confidence >= _HIGH_CONFIDENCE_THRESHOLD:
                direction = "strong follow signal" if pj.verdict == "follow" else "strong ignore signal"
                consensus_worthy.append(
                    SourceDiscoveryJudgePanelConsensusItem(
                        object_key=key,
                        shared_verdict=pj.verdict,
                        primary_confidence=pj.confidence,
                        secondary_confidence=sj.confidence,
                        primary_rationale=pj.rationale,
                        secondary_rationale=sj.rationale,
                        why_consensus=f"Both models assign {pj.verdict} with high combined confidence ({avg_confidence:.2f}); {direction}.",
                    )
                )
        else:
            # Models disagree — classify the divergence type
            primary_low = pj.confidence < _LOW_CONFIDENCE_THRESHOLD
            secondary_low = sj.confidence < _LOW_CONFIDENCE_THRESHOLD

            if primary_low or secondary_low:
                divergence_type = "uncertainty-driven"
                reason = (
                    "One or both models have low confidence; disagreement reflects genuine ambiguity in the signal, "
                    "not model disagreement. A human review may clarify what evidence is missing."
                )
            elif {pj.verdict, sj.verdict} == {"follow", "review"}:
                divergence_type = "conviction-gap"
                reason = (
                    "One model recommends action while the other prefers caution. "
                    "This often means the candidate is promising but under-evidenced; "
                    "worth a time-boxed watch before committing."
                )
            elif {pj.verdict, sj.verdict} == {"review", "ignore"}:
                divergence_type = "threshold-gap"
                reason = (
                    "One model sees enough signal to review while the other sees noise. "
                    "This often means the candidate sits near the relevance boundary; "
                    "worth a manual spot-check to calibrate the discovery filter."
                )
            elif {pj.verdict, sj.verdict} == {"follow", "ignore"}:
                divergence_type = "polarized"
                reason = (
                    "Models are maximally split; this candidate may represent a niche or emerging signal "
                    "that one model recognizes and the other dismisses. High opportunity for discovery "
                    "if a human confirms which model's lens is more appropriate."
                )
            else:
                divergence_type = "asymmetric"
                reason = (
                    "Models disagree with divergent rationales; the candidate may surface differently "
                    "depending on model training recency or domain bias."
                )

            disagreement_worthy.append(
                SourceDiscoveryJudgePanelDisagreementItem(
                    object_key=key,
                    primary_verdict=pj.verdict,
                    secondary_verdict=sj.verdict,
                    primary_confidence=pj.confidence,
                    secondary_confidence=sj.confidence,
                    primary_rationale=pj.rationale,
                    secondary_rationale=sj.rationale,
                    divergence_type=divergence_type,
                    why_opportunity=reason,
                )
            )

    # Derive bounded follow-up hints from the insight distribution
    if not consensus_worthy and not disagreement_worthy:
        follow_up_hints.append("No strong panel signal yet; consider widening the candidate pool or refining the topic.")
    else:
        polarized_count = sum(1 for d in disagreement_worthy if d.divergence_type == "polarized")
        uncertainty_count = sum(1 for d in disagreement_worthy if d.divergence_type == "uncertainty-driven")
        conviction_count = sum(1 for d in disagreement_worthy if d.divergence_type == "conviction-gap")

        if polarized_count > 0:
            follow_up_hints.append(
                f"{polarized_count} polarized split(s) detected — review these candidates manually to resolve which model's lens fits the topic."
            )
        if uncertainty_count > 0:
            follow_up_hints.append(
                f"{uncertainty_count} uncertainty-driven disagreement(s) — gather more evidence before committing."
            )
        if conviction_count > 0:
            follow_up_hints.append(
                f"{conviction_count} conviction-gap candidate(s) — consider a time-boxed watch to confirm signal strength."
            )
        if consensus_worthy:
            follow_up_hints.append(
                f"{len(consensus_worthy)} consensus candidate(s) with high confidence — safe to act on these judgments."
            )

    return SourceDiscoveryJudgePanelInsights(
        consensus_worthy=consensus_worthy,
        disagreement_worthy=disagreement_worthy,
        follow_up_hints=follow_up_hints,
    )


def derive_selective_absorption_advice(
    primary: List[SourceCandidateJudgment],
    secondary: List[SourceCandidateJudgment],
) -> SourceJudgmentSelectiveAbsorptionAdvice:
    """
    Derive bounded controller-facing selective absorption advice.

    This is not a workflow or persisted decision layer. It only suggests which
    panel outcomes are strong enough to follow, suppress, watch, or escalate to
    manual review.
    """
    panel_summary = compare_judgment_verdict_overlap(primary, secondary)
    panel_insights = derive_panel_insights(primary, secondary)

    ready_to_follow: List[SourceJudgmentSelectiveAbsorptionItem] = []
    ready_to_suppress: List[SourceJudgmentSelectiveAbsorptionItem] = []
    needs_manual_review: List[SourceJudgmentSelectiveAbsorptionItem] = []
    watch_candidates: List[SourceJudgmentSelectiveAbsorptionItem] = []
    controller_notes: List[str] = []

    for item in panel_insights.consensus_worthy:
        avg_confidence = (item.primary_confidence + item.secondary_confidence) / 2.0
        advice_item = SourceJudgmentSelectiveAbsorptionItem(
            object_key=item.object_key,
            proposed_action="follow" if item.shared_verdict == "follow" else "suppress",
            basis=f"high_confidence_consensus_{item.shared_verdict}",
            confidence=avg_confidence,
            explanation=item.why_consensus,
        )
        if item.shared_verdict == "follow":
            ready_to_follow.append(advice_item)
        else:
            ready_to_suppress.append(advice_item)

    for item in panel_insights.disagreement_worthy:
        avg_confidence = (item.primary_confidence + item.secondary_confidence) / 2.0
        advice_item = SourceJudgmentSelectiveAbsorptionItem(
            object_key=item.object_key,
            proposed_action="watch" if item.divergence_type == "conviction-gap" else "manual_review",
            basis=item.divergence_type,
            confidence=avg_confidence,
            explanation=item.why_opportunity,
        )
        if item.divergence_type == "conviction-gap":
            watch_candidates.append(advice_item)
        else:
            needs_manual_review.append(advice_item)

    if ready_to_follow:
        controller_notes.append(
            f"{len(ready_to_follow)} high-confidence follow candidate(s) are suitable for bounded controller absorption."
        )
    if ready_to_suppress:
        controller_notes.append(
            f"{len(ready_to_suppress)} high-confidence suppress candidate(s) are suitable for bounded noise compression."
        )
    if watch_candidates:
        controller_notes.append(
            f"{len(watch_candidates)} conviction-gap candidate(s) should stay in a time-boxed watch lane, not immediate absorption."
        )
    if needs_manual_review:
        controller_notes.append(
            f"{len(needs_manual_review)} disagreement candidate(s) require explicit controller review before any absorption."
        )
    if not any((ready_to_follow, ready_to_suppress, watch_candidates, needs_manual_review)):
        controller_notes.append("No bounded selective absorption suggestion yet; keep the panel result inspect-only.")
    elif panel_summary["panel_signal"] == "stable" and not watch_candidates and not needs_manual_review:
        controller_notes.append("Panel output is stable enough for bounded selective absorption, but still remains non-canonical until controller acceptance.")

    return SourceJudgmentSelectiveAbsorptionAdvice(
        ready_to_follow=ready_to_follow,
        ready_to_suppress=ready_to_suppress,
        needs_manual_review=needs_manual_review,
        watch_candidates=watch_candidates,
        controller_notes=controller_notes,
    )
