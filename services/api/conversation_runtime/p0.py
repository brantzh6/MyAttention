from typing import Any, List, Optional

from feeds.ai_judgment import (
    SourceDiscoveryJudgePanelInsights,
    SourceCandidateJudgment,
    SourceJudgmentSelectiveAbsorptionAdvice,
    compare_judgment_verdict_overlap,
    default_model_for_provider,
    derive_panel_insights,
    derive_selective_absorption_advice,
    parse_ai_judgment_payload,
    run_ai_candidate_judgment_once,
)
from conversation_runtime.contracts import (
    ConversationControllerPacket,
    ConversationIntentTrace,
    ConversationOperationalAdvice,
    ConversationPanelIntentTrace,
    ConversationSegmentInspectRequest,
    ConversationSegmentInspectResponse,
    ConversationSegmentPanelInspectRequest,
    ConversationSegmentPanelInspectResponse,
    CorrectionEventJudgment,
    CorrectionEventProposal,
)
from feeds.source_contracts import (
    SourceDiscoveryCandidate,
    SourceDiscoveryFocus,
    SourceDiscoveryInterestBias,
    SourceDiscoveryResponse,
)
from feeds.source_semantics import (
    ai_judgment_truth_boundary,
    candidate_identity,
    focus_category,
)
from feeds.source_postprocess import compress_source_candidates
from feeds.authority import get_authority_classifier
from llm.adapter import LLMAdapter


_ALLOWED_INTENTS = {"source_hint", "correction", "other"}
_ALLOWED_CORRECTION_SCOPES = {
    "source_authority",
    "source_status",
    "source_plan_item",
}
_ALLOWED_CORRECTION_VERDICTS = {"review", "ignore"}
_CONVERSATION_WINDOW_LIMIT = 1600
_CONVERSATION_WINDOW_HEAD = 1000
_CONVERSATION_WINDOW_TAIL = 500


def conversation_truth_boundary() -> List[str]:
    return [
        "raw conversation is not truth",
        "raw conversation is not memory",
        "conversation inspect output is candidate material only",
        "conversation-derived source candidates remain review-gated",
        "conversation-derived corrections are bounded proposals, not accepted state",
        "controller packet is advisory compression, not a workflow contract",
    ]


def _prepare_conversation_window(
    conversation_text: str,
) -> tuple[str, bool]:
    text = conversation_text.strip()
    if len(text) <= _CONVERSATION_WINDOW_LIMIT:
        return text, False
    head = text[:_CONVERSATION_WINDOW_HEAD].rstrip()
    tail = text[-_CONVERSATION_WINDOW_TAIL :].lstrip()
    window = (
        f"{head}\n\n"
        "[conversation window truncated for bounded inspect]\n\n"
        f"{tail}"
    )
    return window, True


def _build_conversation_sample_snippet(conversation_text: str) -> str:
    window, truncated = _prepare_conversation_window(conversation_text)
    if not truncated:
        return window[:200]
    head = window[:100].rstrip()
    tail = window[-80:].lstrip()
    return f"{head} ... [truncated] ... {tail}"


def _build_intent_prompt(body: ConversationSegmentInspectRequest) -> str:
    conversation_window, truncated = _prepare_conversation_window(body.conversation_text)
    return (
        "You are classifying one bounded conversation segment for IKE.\n"
        "Return valid JSON only.\n"
        "Allowed intent values: source_hint, correction, other.\n"
        "If intent=source_hint, extract source_candidates as objects with url and context_note.\n"
        "If intent=correction, extract correction_events with target_scope, target_ref, correction_content.\n"
        "Allowed correction target_scope values: source_authority, source_status, source_plan_item.\n"
        "Do not emit entity/framework/knowledge corrections.\n"
        "Schema:\n"
        "{\n"
        '  "intent": "source_hint|correction|other",\n'
        '  "summary": "short summary",\n'
        '  "source_candidates": [{"url": "...", "context_note": "..."}],\n'
        '  "correction_events": [{"target_scope": "...", "target_ref": "...", "correction_content": "..."}]\n'
        "}\n\n"
        f"Topic: {body.topic}\n"
        f"Task intent: {body.task_intent}\n"
        f"Focus: {body.focus.value}\n"
        f"Speaker role: {body.speaker_role}\n"
        f"Conversation window truncated: {'yes' if truncated else 'no'}\n"
        f"Conversation:\n{conversation_window}\n"
    )


def _build_correction_judgment_prompt(
    body: ConversationSegmentInspectRequest,
    correction_events: List[CorrectionEventProposal],
) -> str:
    conversation_window, truncated = _prepare_conversation_window(body.conversation_text)
    correction_block = [
        {
            "target_scope": event.target_scope,
            "target_ref": event.target_ref,
            "correction_content": event.correction_content,
        }
        for event in correction_events
    ]
    return (
        "You are reviewing bounded conversation-derived source correction proposals for IKE.\n"
        "Return valid JSON only.\n"
        "This is advisory review, not canonical acceptance.\n"
        "Allowed verdict values: review, ignore.\n"
        "Use review when the correction is plausible and deserves controller attention.\n"
        "Use ignore when the correction is too weak, too vague, or not worth acting on now.\n"
        "Schema:\n"
        "{\n"
        '  "summary": "short summary",\n'
        '  "judgments": [\n'
        "    {\n"
        '      "target_scope": "source_authority|source_status|source_plan_item",\n'
        '      "target_ref": "proposal target_ref",\n'
        '      "correction_content": "proposal correction_content",\n'
        '      "verdict": "review|ignore",\n'
        '      "rationale": "why",\n'
        '      "confidence": 0.0\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"Topic: {body.topic}\n"
        f"Task intent: {body.task_intent}\n"
        f"Focus: {body.focus.value}\n"
        f"Conversation window truncated: {'yes' if truncated else 'no'}\n"
        f"Conversation:\n{conversation_window}\n\n"
        f"Correction proposals:\n{correction_block}"
    )


def _normalize_intent(value: Any) -> str:
    normalized = str(value or "other").strip().lower()
    return normalized if normalized in _ALLOWED_INTENTS else "other"


def _build_source_candidate(
    url: str,
    context_note: str,
    body: ConversationSegmentInspectRequest,
) -> Optional[SourceDiscoveryCandidate]:
    normalized_url = str(url or "").strip()
    if not normalized_url:
        return None
    item_type, object_key, display_name, canonical_url, source_domain = candidate_identity(
        normalized_url, body.focus
    )
    authority = get_authority_classifier().classify(
        canonical_url,
        context_note or display_name,
        focus_category(body.focus),
    )
    return SourceDiscoveryCandidate(
        item_type=item_type,
        object_key=object_key,
        domain=source_domain,
        name=display_name,
        url=canonical_url,
        authority_tier=authority.tier,
        authority_score=authority.score,
        recommendation="review",
        recommendation_reason="conversation-derived source hint",
        evidence_count=1,
        matched_queries=[body.topic],
        sample_titles=[context_note or display_name],
        sample_snippets=[_build_conversation_sample_snippet(body.conversation_text)],
        source_nature="conversation_hint",
        temperature="medium",
        recommended_mode="inspect",
        recommended_execution_strategy="review_first",
        why_relevant=context_note or "derived from bounded conversation segment",
        confidence_note="single-segment conversation extraction",
        canonical_ref=object_key,
        candidate_endpoints=[canonical_url],
    )


def _normalize_correction_events(payload: dict[str, Any]) -> tuple[List[CorrectionEventProposal], int]:
    events: List[CorrectionEventProposal] = []
    raw_events = list(payload.get("correction_events", []))
    for raw in raw_events:
        if not isinstance(raw, dict):
            continue
        target_scope = str(raw.get("target_scope", "")).strip().lower()
        target_ref = str(raw.get("target_ref", "")).strip()
        correction_content = str(raw.get("correction_content", "")).strip()
        if target_scope not in _ALLOWED_CORRECTION_SCOPES:
            continue
        if not target_ref or not correction_content:
            continue
        events.append(
            CorrectionEventProposal(
                target_scope=target_scope,
                target_ref=target_ref,
                correction_content=correction_content,
                provenance_note="conversation-segment-derived",
            )
        )
    discarded = max(0, len(raw_events) - len(events))
    return events, discarded


def _normalize_correction_judgments(
    correction_events: List[CorrectionEventProposal],
    payload: dict[str, Any],
) -> tuple[List[CorrectionEventJudgment], str, int]:
    allowed = {
        (event.target_scope, event.target_ref, event.correction_content)
        for event in correction_events
    }
    summary = str(payload.get("summary", "") or "").strip()
    judgments: List[CorrectionEventJudgment] = []
    raw_judgments = list(payload.get("judgments", []))
    for raw in raw_judgments:
        if not isinstance(raw, dict):
            continue
        target_scope = str(raw.get("target_scope", "")).strip().lower()
        target_ref = str(raw.get("target_ref", "")).strip()
        correction_content = str(raw.get("correction_content", "")).strip()
        verdict = str(raw.get("verdict", "")).strip().lower()
        if (target_scope, target_ref, correction_content) not in allowed:
            continue
        if verdict not in _ALLOWED_CORRECTION_VERDICTS:
            continue
        try:
            confidence = float(raw.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        judgments.append(
            CorrectionEventJudgment(
                target_scope=target_scope,
                target_ref=target_ref,
                correction_content=correction_content,
                verdict=verdict,
                rationale=str(raw.get("rationale", "") or "").strip(),
                confidence=max(0.0, min(1.0, confidence)),
            )
        )
    discarded = max(0, len(raw_judgments) - len(judgments))
    return judgments, summary, discarded


async def _run_correction_judgment_once(
    *,
    adapter: LLMAdapter,
    provider: str,
    model: str,
    body: ConversationSegmentInspectRequest,
    correction_events: List[CorrectionEventProposal],
) -> tuple[List[CorrectionEventJudgment], str, str, int]:
    raw = await adapter.chat(
        message=_build_correction_judgment_prompt(body, correction_events),
        provider=provider,
        model=model,
        system_prompt="Return valid JSON only.",
    )
    payload, parse_status = parse_ai_judgment_payload(raw)
    judgments, summary, discarded = _normalize_correction_judgments(
        correction_events,
        payload,
    )
    return judgments, summary, parse_status, discarded


def _correction_judgment_key(judgment: CorrectionEventJudgment) -> str:
    return f"{judgment.target_scope}|{judgment.target_ref}|{judgment.correction_content}"


def _compare_correction_judgment_overlap(
    primary: List[CorrectionEventJudgment],
    secondary: List[CorrectionEventJudgment],
) -> dict[str, Any]:
    primary_map = {_correction_judgment_key(judgment): judgment.verdict for judgment in primary}
    secondary_map = {_correction_judgment_key(judgment): judgment.verdict for judgment in secondary}
    shared_keys = sorted(set(primary_map) & set(secondary_map))
    agreed = [key for key in shared_keys if primary_map[key] == secondary_map[key]]
    disagreed = [key for key in shared_keys if primary_map[key] != secondary_map[key]]
    primary_only = sorted(set(primary_map) - set(secondary_map))
    secondary_only = sorted(set(secondary_map) - set(primary_map))
    return {
        "shared_corrections": len(shared_keys),
        "agreement_count": len(agreed),
        "disagreement_count": len(disagreed),
        "primary_only_count": len(primary_only),
        "secondary_only_count": len(secondary_only),
        "panel_signal": (
            "stable"
            if shared_keys and not disagreed and not primary_only and not secondary_only
            else "mixed"
        ),
    }


def _merge_source_candidates(
    primary: List[SourceDiscoveryCandidate],
    secondary: List[SourceDiscoveryCandidate],
    max_candidates: int,
) -> List[SourceDiscoveryCandidate]:
    merged: List[SourceDiscoveryCandidate] = []
    seen: set[str] = set()
    for candidate in list(primary) + list(secondary):
        if candidate.object_key in seen:
            continue
        seen.add(candidate.object_key)
        merged.append(candidate)
        if len(merged) >= max_candidates:
            break
    return merged


def _compress_conversation_source_candidates(
    candidates: List[SourceDiscoveryCandidate],
    focus: SourceDiscoveryFocus,
    max_candidates: int,
) -> List[SourceDiscoveryCandidate]:
    compressed = compress_source_candidates(candidates, focus)
    return compressed[:max_candidates]


def _dropped_source_object_keys(
    before: List[SourceDiscoveryCandidate],
    after: List[SourceDiscoveryCandidate],
) -> List[str]:
    after_keys = {candidate.object_key for candidate in after}
    dropped: List[str] = []
    for candidate in before:
        if candidate.object_key not in after_keys and candidate.object_key not in dropped:
            dropped.append(candidate.object_key)
    return dropped


def _merge_correction_events(
    primary: List[CorrectionEventProposal],
    secondary: List[CorrectionEventProposal],
) -> List[CorrectionEventProposal]:
    merged: List[CorrectionEventProposal] = []
    seen: set[tuple[str, str, str]] = set()
    for event in list(primary) + list(secondary):
        key = (event.target_scope, event.target_ref, event.correction_content)
        if key in seen:
            continue
        seen.add(key)
        merged.append(event)
    return merged


def _summarize_extraction_overlap(
    primary_intent: str,
    secondary_intent: str,
    primary_candidates: List[SourceDiscoveryCandidate],
    secondary_candidates: List[SourceDiscoveryCandidate],
    merged_candidates: List[SourceDiscoveryCandidate],
    primary_corrections: List[CorrectionEventProposal],
    secondary_corrections: List[CorrectionEventProposal],
    merged_corrections: List[CorrectionEventProposal],
) -> dict[str, Any]:
    primary_keys = {candidate.object_key for candidate in primary_candidates}
    secondary_keys = {candidate.object_key for candidate in secondary_candidates}
    shared_keys = sorted(primary_keys & secondary_keys)
    primary_only = sorted(primary_keys - secondary_keys)
    secondary_only = sorted(secondary_keys - primary_keys)

    primary_correction_keys = {
        (event.target_scope, event.target_ref, event.correction_content)
        for event in primary_corrections
    }
    secondary_correction_keys = {
        (event.target_scope, event.target_ref, event.correction_content)
        for event in secondary_corrections
    }
    correction_shared = len(primary_correction_keys & secondary_correction_keys)

    return {
        "intent_signal": "stable" if primary_intent == secondary_intent else "mixed",
        "primary_intent": primary_intent,
        "secondary_intent": secondary_intent,
        "source_candidate_signal": (
            "stable"
            if primary_keys == secondary_keys
            else "mixed"
        ),
        "primary_source_candidate_count": len(primary_candidates),
        "secondary_source_candidate_count": len(secondary_candidates),
        "merged_source_candidate_count": len(merged_candidates),
        "shared_source_candidate_count": len(shared_keys),
        "primary_only_source_candidate_count": len(primary_only),
        "secondary_only_source_candidate_count": len(secondary_only),
        "correction_signal": (
            "stable"
            if primary_correction_keys == secondary_correction_keys
            else "mixed"
        ),
        "primary_correction_count": len(primary_corrections),
        "secondary_correction_count": len(secondary_corrections),
        "merged_correction_count": len(merged_corrections),
        "shared_correction_count": correction_shared,
    }


def _derive_single_lane_operational_advice(
    source_judgments: List[SourceCandidateJudgment],
    correction_events: List[CorrectionEventProposal],
    correction_judgments: List[CorrectionEventJudgment],
    segment_intent: str,
) -> ConversationOperationalAdvice:
    notes: List[str] = []
    follow_count = sum(1 for judgment in source_judgments if judgment.verdict == "follow")
    review_count = sum(1 for judgment in source_judgments if judgment.verdict == "review")
    correction_review_count = sum(
        1 for judgment in correction_judgments if judgment.verdict == "review"
    )

    if correction_events:
        notes.append("bounded source-related corrections were extracted and should remain review-gated")
    if correction_review_count:
        notes.append("at least one correction proposal is worth controller review")
    if follow_count:
        notes.append("at least one source candidate is worth follow-up review")
    if review_count:
        notes.append("some source candidates still require manual review")

    if follow_count:
        next_step = "review_source_candidates"
    elif correction_review_count:
        next_step = "review_corrections"
    elif segment_intent == "other":
        next_step = "no_action"
        notes.append("segment classified as other; no candidate promotion should occur")
    elif correction_events:
        next_step = "manual_review"
        notes.append("correction proposals exist but none are strong enough for immediate review")
    else:
        next_step = "manual_review"
        notes.append("segment produced bounded candidates but no clear follow signal")

    return ConversationOperationalAdvice(
        suggested_next_step=next_step,
        controller_notes=notes,
    )


def _derive_panel_operational_advice(
    extraction_summary: dict[str, Any],
    panel_summary: dict[str, Any],
    correction_panel_summary: dict[str, Any],
    selective_absorption: SourceJudgmentSelectiveAbsorptionAdvice,
    correction_events: List[CorrectionEventProposal],
    primary_correction_judgments: List[CorrectionEventJudgment],
    secondary_correction_judgments: List[CorrectionEventJudgment],
    segment_intent: str,
    lane_incomplete: bool,
) -> ConversationOperationalAdvice:
    notes: List[str] = []
    ready_follow = len(selective_absorption.ready_to_follow)
    manual_review = len(selective_absorption.needs_manual_review)
    watch_count = len(selective_absorption.watch_candidates)
    correction_review_count = sum(
        1 for judgment in list(primary_correction_judgments) + list(secondary_correction_judgments)
        if judgment.verdict == "review"
    )
    extraction_mixed = bool(extraction_summary) and (
        extraction_summary.get("intent_signal") == "mixed"
        or extraction_summary.get("source_candidate_signal") == "mixed"
        or extraction_summary.get("correction_signal") == "mixed"
    )
    correction_panel_mixed = bool(correction_panel_summary) and (
        correction_panel_summary.get("panel_signal") == "mixed"
    )
    correction_panel_stable_review = bool(correction_panel_summary) and (
        correction_panel_summary.get("panel_signal") == "stable"
        and correction_review_count > 0
    )

    if ready_follow:
        notes.append("panel surfaced candidates that are ready for controller follow-up")
    if manual_review:
        notes.append("panel disagreement or caution indicates manual review remains necessary")
    if watch_count:
        notes.append("panel surfaced watch candidates rather than immediate follow decisions")
    if correction_events:
        notes.append("source-related correction proposals remain inspect-only and require review")
    if correction_review_count:
        notes.append("panel surfaced correction proposals that are worth controller review")
    if extraction_summary:
        notes.append(
            f"extraction source-candidate signal is {extraction_summary.get('source_candidate_signal', 'unknown')}"
        )
        if extraction_summary.get("intent_signal") == "mixed":
            notes.append("models disagreed on segment intent classification")
        if extraction_mixed:
            notes.append("extraction divergence should be treated as an opportunity for controller review")
    if panel_summary:
        notes.append(f"panel signal is {panel_summary.get('panel_signal', 'unknown')}")
    if correction_panel_summary:
        notes.append(
            f"correction panel signal is {correction_panel_summary.get('panel_signal', 'unknown')}"
        )
    if lane_incomplete:
        notes.append("one or more panel lanes were incomplete; controller review is required")

    if ready_follow and not extraction_mixed:
        next_step = "review_ready_to_follow"
    elif correction_panel_stable_review and not extraction_mixed and not lane_incomplete:
        next_step = "review_corrections"
    elif (
        ready_follow
        or lane_incomplete
        or manual_review
        or watch_count
        or correction_review_count
        or correction_events
        or extraction_mixed
        or correction_panel_mixed
    ):
        next_step = "manual_review"
    elif segment_intent == "other":
        next_step = "no_action"
        notes.append("segment classified as other; panel output should not trigger promotion")
    else:
        next_step = "no_action"
        notes.append("no bounded operational action is justified from this segment")

    return ConversationOperationalAdvice(
        suggested_next_step=next_step,
        controller_notes=notes,
    )


def _build_single_lane_controller_packet(
    source_judgments: List[SourceCandidateJudgment],
    correction_judgments: List[CorrectionEventJudgment],
    operational_advice: ConversationOperationalAdvice,
) -> ConversationControllerPacket:
    actionable_source_object_keys = [
        judgment.object_key
        for judgment in source_judgments
        if judgment.verdict == "follow"
    ]
    actionable_correction_targets = [
        f"{judgment.target_scope}:{judgment.target_ref}"
        for judgment in correction_judgments
        if judgment.verdict == "review"
    ]
    reason_tags: List[str] = []
    if actionable_source_object_keys:
        reason_tags.append("source_follow")
    if actionable_correction_targets:
        reason_tags.append("correction_review")
    if operational_advice.suggested_next_step == "manual_review":
        reason_tags.append("manual_review_required")
    if not reason_tags:
        reason_tags.append("no_action")
    return ConversationControllerPacket(
        review_mode=operational_advice.suggested_next_step,
        actionable_source_object_keys=actionable_source_object_keys,
        actionable_correction_targets=actionable_correction_targets,
        reason_tags=reason_tags,
        advisory_scope="inspect_compression_only",
        truth_status="non_canonical",
    )


def _build_panel_controller_packet(
    selective_absorption: SourceJudgmentSelectiveAbsorptionAdvice,
    primary_correction_judgments: List[CorrectionEventJudgment],
    secondary_correction_judgments: List[CorrectionEventJudgment],
    operational_advice: ConversationOperationalAdvice,
) -> ConversationControllerPacket:
    actionable_source_object_keys = [
        item.object_key for item in selective_absorption.ready_to_follow
    ]
    reviewable_corrections: set[str] = set()
    for judgment in list(primary_correction_judgments) + list(secondary_correction_judgments):
        if judgment.verdict == "review":
            reviewable_corrections.add(f"{judgment.target_scope}:{judgment.target_ref}")
    reason_tags: List[str] = []
    if actionable_source_object_keys:
        reason_tags.append("source_ready_to_follow")
    if reviewable_corrections:
        reason_tags.append("correction_review")
    if operational_advice.suggested_next_step == "manual_review":
        reason_tags.append("manual_review_required")
    if operational_advice.suggested_next_step == "review_corrections":
        reason_tags.append("stable_correction_panel")
    if not reason_tags:
        reason_tags.append("no_action")
    return ConversationControllerPacket(
        review_mode=operational_advice.suggested_next_step,
        actionable_source_object_keys=actionable_source_object_keys,
        actionable_correction_targets=sorted(reviewable_corrections),
        reason_tags=reason_tags,
        advisory_scope="inspect_compression_only",
        truth_status="non_canonical",
    )


async def run_conversation_segment_inspect(
    body: ConversationSegmentInspectRequest,
) -> ConversationSegmentInspectResponse:
    adapter = LLMAdapter()
    model = body.model.strip() or default_model_for_provider(body.provider)
    _, conversation_window_truncated = _prepare_conversation_window(body.conversation_text)
    raw = await adapter.chat(
        message=_build_intent_prompt(body),
        provider=body.provider,
        model=model,
        system_prompt="Return valid JSON only.",
    )
    payload, parse_status = parse_ai_judgment_payload(raw)
    segment_intent = _normalize_intent(payload.get("intent"))
    source_candidates: List[SourceDiscoveryCandidate] = []
    raw_candidates = list(payload.get("source_candidates", []))
    for raw_candidate in raw_candidates[: body.max_source_candidates]:
        if not isinstance(raw_candidate, dict):
            continue
        candidate = _build_source_candidate(
            url=str(raw_candidate.get("url", "")).strip(),
            context_note=str(raw_candidate.get("context_note", "")).strip(),
            body=body,
        )
        if candidate is not None:
            source_candidates.append(candidate)
    precompression_source_candidates = list(source_candidates)
    source_candidates = _compress_conversation_source_candidates(
        source_candidates,
        body.focus,
        body.max_source_candidates,
    )
    discarded_source_candidates = max(0, len(raw_candidates) - len(source_candidates))
    correction_events, discarded_corrections = _normalize_correction_events(payload)

    source_judgments: List[SourceCandidateJudgment] = []
    source_summary = ""
    source_judgment_parse_status = "not_run"
    source_discarded_judgments = 0
    correction_judgments: List[CorrectionEventJudgment] = []
    correction_summary = ""
    correction_judgment_parse_status = "not_run"
    correction_discarded_judgments = 0
    if source_candidates:
        discovery = SourceDiscoveryResponse(
            topic=body.topic,
            focus=body.focus,
            task_intent=body.task_intent,
            interest_bias=body.interest_bias
            or SourceDiscoveryInterestBias.AUTHORITY,
            queries=[],
            notes=["conversation_segment"],
            truth_boundary=conversation_truth_boundary(),
            candidates=source_candidates,
        )
        (
            source_judgments,
            source_summary,
            source_judgment_parse_status,
            source_discarded_judgments,
        ) = await run_ai_candidate_judgment_once(
            adapter=adapter,
            provider=body.provider,
            model=model,
            topic=discovery.topic,
            focus=discovery.focus,
            task_intent=discovery.task_intent,
            interest_bias=discovery.interest_bias,
            judged_candidates=source_candidates,
        )
    if correction_events:
        (
            correction_judgments,
            correction_summary,
            correction_judgment_parse_status,
            correction_discarded_judgments,
        ) = await _run_correction_judgment_once(
            adapter=adapter,
            provider=body.provider,
            model=model,
            body=body,
            correction_events=correction_events,
        )

    notes = [
        f"conversation_parse_status={parse_status}",
        f"segment_intent={segment_intent}",
        f"source_candidates={len(source_candidates)}",
        f"discarded_source_candidates={discarded_source_candidates}",
        f"correction_events={len(correction_events)}",
        f"discarded_corrections={discarded_corrections}",
        f"source_judgment_parse_status={source_judgment_parse_status}",
        f"discarded_judgments={source_discarded_judgments}",
        f"correction_judgment_parse_status={correction_judgment_parse_status}",
        f"discarded_correction_judgments={correction_discarded_judgments}",
        f"conversation_window_truncated={str(conversation_window_truncated).lower()}",
    ]
    truth_boundary = conversation_truth_boundary()
    truth_boundary.extend(ai_judgment_truth_boundary())
    truth_boundary.append(
        "conversation inspect does not auto-promote candidates or corrections into canonical truth"
    )
    truth_boundary.append(
        "correction judgments are advisory review signals, not accepted correction state"
    )
    truth_boundary.append(
        "controller packet is advisory compression only and must not be treated as an execution or promotion contract"
    )
    operational_advice = _derive_single_lane_operational_advice(
        source_judgments=source_judgments,
        correction_events=correction_events,
        correction_judgments=correction_judgments,
        segment_intent=segment_intent,
    )
    controller_packet = _build_single_lane_controller_packet(
        source_judgments=source_judgments,
        correction_judgments=correction_judgments,
        operational_advice=operational_advice,
    )
    intent_trace = ConversationIntentTrace(
        raw_segment_intent=segment_intent,
        source_candidates_before_compression=len(precompression_source_candidates),
        source_candidates_after_compression=len(source_candidates),
        dropped_source_object_keys=_dropped_source_object_keys(
            precompression_source_candidates,
            source_candidates,
        ),
        correction_events_extracted=len(correction_events),
        conversation_window_truncated=conversation_window_truncated,
    )
    return ConversationSegmentInspectResponse(
        topic=body.topic,
        task_intent=body.task_intent,
        focus=body.focus,
        interest_bias=body.interest_bias
        or SourceDiscoveryInterestBias.AUTHORITY,
        provider=body.provider,
        model=model,
        segment_intent=segment_intent,
        source_candidates=source_candidates,
        source_judgments=source_judgments,
        source_summary=source_summary,
        correction_events=correction_events,
        correction_judgments=correction_judgments,
        correction_summary=correction_summary,
        operational_advice=operational_advice,
        controller_packet=controller_packet,
        intent_trace=intent_trace,
        notes=notes,
        truth_boundary=truth_boundary,
    )


async def run_conversation_segment_panel_inspect(
    body: ConversationSegmentPanelInspectRequest,
) -> ConversationSegmentPanelInspectResponse:
    adapter = LLMAdapter()
    _, conversation_window_truncated = _prepare_conversation_window(body.conversation_text)
    primary_model = body.primary_model.strip() or default_model_for_provider(
        body.primary_provider
    )
    secondary_model = body.secondary_model.strip() or default_model_for_provider(
        body.secondary_provider
    )

    base_request = ConversationSegmentInspectRequest(
        conversation_text=body.conversation_text,
        speaker_role=body.speaker_role,
        topic=body.topic,
        task_intent=body.task_intent,
        focus=body.focus,
        interest_bias=body.interest_bias,
        thread_id=body.thread_id,
        provider=body.primary_provider,
        model=primary_model,
        max_source_candidates=body.max_source_candidates,
    )
    primary_raw = await adapter.chat(
        message=_build_intent_prompt(base_request),
        provider=body.primary_provider,
        model=primary_model,
        system_prompt="Return valid JSON only.",
    )
    secondary_raw = await adapter.chat(
        message=_build_intent_prompt(base_request),
        provider=body.secondary_provider,
        model=secondary_model,
        system_prompt="Return valid JSON only.",
    )
    primary_payload, primary_extraction_parse_status = parse_ai_judgment_payload(primary_raw)
    secondary_payload, secondary_extraction_parse_status = parse_ai_judgment_payload(secondary_raw)
    primary_intent = _normalize_intent(primary_payload.get("intent"))
    secondary_intent = _normalize_intent(secondary_payload.get("intent"))
    segment_intent = primary_intent

    primary_source_candidates: List[SourceDiscoveryCandidate] = []
    primary_raw_candidates = list(primary_payload.get("source_candidates", []))
    for raw_candidate in primary_raw_candidates[: body.max_source_candidates]:
        if not isinstance(raw_candidate, dict):
            continue
        candidate = _build_source_candidate(
            url=str(raw_candidate.get("url", "")).strip(),
            context_note=str(raw_candidate.get("context_note", "")).strip(),
            body=base_request,
        )
        if candidate is not None:
            primary_source_candidates.append(candidate)
    secondary_source_candidates: List[SourceDiscoveryCandidate] = []
    secondary_raw_candidates = list(secondary_payload.get("source_candidates", []))
    for raw_candidate in secondary_raw_candidates[: body.max_source_candidates]:
        if not isinstance(raw_candidate, dict):
            continue
        candidate = _build_source_candidate(
            url=str(raw_candidate.get("url", "")).strip(),
            context_note=str(raw_candidate.get("context_note", "")).strip(),
            body=base_request,
        )
        if candidate is not None:
            secondary_source_candidates.append(candidate)

    source_candidates = _merge_source_candidates(
        primary_source_candidates,
        secondary_source_candidates,
        body.max_source_candidates,
    )
    precompression_source_candidates = list(source_candidates)
    source_candidates = _compress_conversation_source_candidates(
        source_candidates,
        body.focus,
        body.max_source_candidates,
    )
    discarded_source_candidates = max(
        0,
        len(primary_raw_candidates) + len(secondary_raw_candidates) - len(source_candidates),
    )
    primary_correction_events, primary_discarded_corrections = _normalize_correction_events(primary_payload)
    secondary_correction_events, secondary_discarded_corrections = _normalize_correction_events(secondary_payload)
    correction_events = _merge_correction_events(
        primary_correction_events,
        secondary_correction_events,
    )
    discarded_corrections = (
        primary_discarded_corrections + secondary_discarded_corrections
    )

    primary_judgments: List[SourceCandidateJudgment] = []
    secondary_judgments: List[SourceCandidateJudgment] = []
    primary_summary = ""
    secondary_summary = ""
    primary_parse_status = "not_run"
    secondary_parse_status = "not_run"
    primary_discarded = 0
    secondary_discarded = 0
    panel_summary: dict[str, Any] = {}
    extraction_summary: dict[str, Any] = _summarize_extraction_overlap(
        primary_intent=primary_intent,
        secondary_intent=secondary_intent,
        primary_candidates=primary_source_candidates,
        secondary_candidates=secondary_source_candidates,
        merged_candidates=source_candidates,
        primary_corrections=primary_correction_events,
        secondary_corrections=secondary_correction_events,
        merged_corrections=correction_events,
    )
    panel_insights = SourceDiscoveryJudgePanelInsights()
    selective_absorption = SourceJudgmentSelectiveAbsorptionAdvice()
    primary_correction_judgments: List[CorrectionEventJudgment] = []
    secondary_correction_judgments: List[CorrectionEventJudgment] = []
    primary_correction_summary = ""
    secondary_correction_summary = ""
    primary_correction_parse_status = "not_run"
    secondary_correction_parse_status = "not_run"
    primary_correction_discarded = 0
    secondary_correction_discarded = 0
    correction_panel_summary: dict[str, Any] = {}

    if source_candidates:
        discovery = SourceDiscoveryResponse(
            topic=body.topic,
            focus=body.focus,
            task_intent=body.task_intent,
            interest_bias=body.interest_bias
            or SourceDiscoveryInterestBias.AUTHORITY,
            queries=[],
            notes=["conversation_segment"],
            truth_boundary=conversation_truth_boundary(),
            candidates=source_candidates,
        )
        (
            primary_judgments,
            primary_summary,
            primary_parse_status,
            primary_discarded,
        ) = await run_ai_candidate_judgment_once(
            adapter=adapter,
            provider=body.primary_provider,
            model=primary_model,
            topic=discovery.topic,
            focus=discovery.focus,
            task_intent=discovery.task_intent,
            interest_bias=discovery.interest_bias,
            judged_candidates=source_candidates,
        )
        (
            secondary_judgments,
            secondary_summary,
            secondary_parse_status,
            secondary_discarded,
        ) = await run_ai_candidate_judgment_once(
            adapter=adapter,
            provider=body.secondary_provider,
            model=secondary_model,
            topic=discovery.topic,
            focus=discovery.focus,
            task_intent=discovery.task_intent,
            interest_bias=discovery.interest_bias,
            judged_candidates=source_candidates,
        )
        panel_summary = compare_judgment_verdict_overlap(
            primary_judgments, secondary_judgments
        )
        panel_insights = derive_panel_insights(primary_judgments, secondary_judgments)
        selective_absorption = derive_selective_absorption_advice(
            primary_judgments, secondary_judgments
        )

    if correction_events:
        (
            primary_correction_judgments,
            primary_correction_summary,
            primary_correction_parse_status,
            primary_correction_discarded,
        ) = await _run_correction_judgment_once(
            adapter=adapter,
            provider=body.primary_provider,
            model=primary_model,
            body=base_request,
            correction_events=correction_events,
        )
        (
            secondary_correction_judgments,
            secondary_correction_summary,
            secondary_correction_parse_status,
            secondary_correction_discarded,
        ) = await _run_correction_judgment_once(
            adapter=adapter,
            provider=body.secondary_provider,
            model=secondary_model,
            body=base_request,
            correction_events=correction_events,
        )
        correction_panel_summary = _compare_correction_judgment_overlap(
            primary_correction_judgments,
            secondary_correction_judgments,
        )

    notes = [
        f"primary_extraction_parse_status={primary_extraction_parse_status}",
        f"secondary_extraction_parse_status={secondary_extraction_parse_status}",
        f"segment_intent={segment_intent}",
        f"secondary_segment_intent={secondary_intent}",
        f"source_candidates={len(source_candidates)}",
        f"discarded_source_candidates={discarded_source_candidates}",
        f"correction_events={len(correction_events)}",
        f"discarded_corrections={discarded_corrections}",
        f"primary_parse_status={primary_parse_status}",
        f"primary_discarded_judgments={primary_discarded}",
        f"secondary_parse_status={secondary_parse_status}",
        f"secondary_discarded_judgments={secondary_discarded}",
        f"primary_correction_parse_status={primary_correction_parse_status}",
        f"primary_discarded_correction_judgments={primary_correction_discarded}",
        f"secondary_correction_parse_status={secondary_correction_parse_status}",
        f"secondary_discarded_correction_judgments={secondary_correction_discarded}",
        f"conversation_window_truncated={str(conversation_window_truncated).lower()}",
    ]
    if panel_summary:
        notes.extend(
            [
                f"panel_signal={panel_summary['panel_signal']}",
                f"panel_agreement_count={panel_summary['agreement_count']}",
                f"panel_disagreement_count={panel_summary['disagreement_count']}",
            ]
        )
    if correction_panel_summary:
        notes.extend(
            [
                f"correction_panel_signal={correction_panel_summary['panel_signal']}",
                f"correction_panel_agreement_count={correction_panel_summary['agreement_count']}",
                f"correction_panel_disagreement_count={correction_panel_summary['disagreement_count']}",
            ]
        )
    truth_boundary = conversation_truth_boundary()
    truth_boundary.extend(ai_judgment_truth_boundary())
    truth_boundary.append(
        "conversation panel inspect exposes agreement shape, not a merged canonical verdict"
    )
    truth_boundary.append(
        "selective_absorption is advisory controller guidance, not automatic promotion or persistence"
    )
    truth_boundary.append(
        "correction panel output is advisory review shape, not accepted correction state"
    )
    truth_boundary.append(
        "controller packet is advisory compression only and must not be treated as an execution or promotion contract"
    )
    operational_advice = _derive_panel_operational_advice(
        extraction_summary=extraction_summary,
        panel_summary=panel_summary,
        correction_panel_summary=correction_panel_summary,
        selective_absorption=selective_absorption,
        correction_events=correction_events,
        primary_correction_judgments=primary_correction_judgments,
        secondary_correction_judgments=secondary_correction_judgments,
        segment_intent=segment_intent,
        lane_incomplete=(
            (
                bool(source_candidates)
                and (
                    primary_parse_status != "valid_json"
                    or secondary_parse_status != "valid_json"
                    or primary_extraction_parse_status != "valid_json"
                    or secondary_extraction_parse_status != "valid_json"
                )
            )
            or (
                bool(correction_events)
                and (
                    primary_correction_parse_status != "valid_json"
                    or secondary_correction_parse_status != "valid_json"
                )
            )
        ),
    )
    controller_packet = _build_panel_controller_packet(
        selective_absorption=selective_absorption,
        primary_correction_judgments=primary_correction_judgments,
        secondary_correction_judgments=secondary_correction_judgments,
        operational_advice=operational_advice,
    )
    intent_trace = ConversationPanelIntentTrace(
        primary_raw_intent=primary_intent,
        secondary_raw_intent=secondary_intent,
        merged_segment_intent=segment_intent,
        source_candidates_before_compression=len(precompression_source_candidates),
        source_candidates_after_compression=len(source_candidates),
        dropped_source_object_keys=_dropped_source_object_keys(
            precompression_source_candidates,
            source_candidates,
        ),
        correction_events_before_merge=(
            len(primary_correction_events) + len(secondary_correction_events)
        ),
        correction_events_after_merge=len(correction_events),
        conversation_window_truncated=conversation_window_truncated,
    )
    return ConversationSegmentPanelInspectResponse(
        topic=body.topic,
        task_intent=body.task_intent,
        focus=body.focus,
        interest_bias=body.interest_bias
        or SourceDiscoveryInterestBias.AUTHORITY,
        primary_provider=body.primary_provider,
        primary_model=primary_model,
        secondary_provider=body.secondary_provider,
        secondary_model=secondary_model,
        segment_intent=segment_intent,
        source_candidates=source_candidates,
        primary_judgments=primary_judgments,
        secondary_judgments=secondary_judgments,
        primary_summary=primary_summary,
        secondary_summary=secondary_summary,
        extraction_summary=extraction_summary,
        panel_summary=panel_summary,
        panel_insights=panel_insights,
        selective_absorption=selective_absorption,
        correction_events=correction_events,
        primary_correction_judgments=primary_correction_judgments,
        secondary_correction_judgments=secondary_correction_judgments,
        primary_correction_summary=primary_correction_summary,
        secondary_correction_summary=secondary_correction_summary,
        correction_panel_summary=correction_panel_summary,
        operational_advice=operational_advice,
        controller_packet=controller_packet,
        intent_trace=intent_trace,
        notes=notes,
        truth_boundary=truth_boundary,
    )
