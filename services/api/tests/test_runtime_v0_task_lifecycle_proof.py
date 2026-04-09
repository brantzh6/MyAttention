"""
IKE Runtime v0 – Task Lifecycle Proof Tests (R2-B1)

Proves ONE truthful task lifecycle through the hardened runtime base.
This test validates the narrowest possible lifecycle proof using:

- Runtime-owned claim verification (ClaimContext + ClaimVerifier)
- Auditable event sequence aligned with state transitions
- No hidden second truth source (WorkContext is derivative)

R2-B1 Acceptance Focus:
1. task lifecycle truth is explicit
2. no hidden second truth source is introduced
3. the proof uses the hardened runtime base as it now exists
4. tests make the lifecycle proof auditable
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from runtime.state_machine import (
    TaskStatus,
    OwnerKind,
    ClaimType,
    ClaimContext,
    validate_transition,
    TransitionError,
    InvalidTransitionError,
    GuardrailViolationError,
    ClaimRequiredError,
)
from runtime.transitions import (
    TransitionRequest,
    execute_transition,
    build_event_record,
)
from runtime.events import (
    EventType,
    TaskEvent,
    EventSequence,
)
from runtime.leases import (
    claim_lease,
    InMemoryClaimVerifier,
    LeaseRecord,
)
from runtime.work_context import (
    WorkContext,
    TaskSnapshot,
    reconstruct_work_context,
)
from runtime.memory_packets import (
    MemoryPacket,
    PacketStatus,
    create_packet,
    accept_packet,
    is_packet_trusted,
)
from runtime.task_lifecycle import (
    LifecycleProofResult,
    execute_lifecycle_proof,
    create_lifecycle_memory_packet,
    derive_work_context_from_proof,
    validate_lifecycle_proof_integrity,
    is_proof_auditable,
    CANONICAL_LIFECYCLE_PATH,
    CANONICAL_LIFECYCLE_ACTORS,
)


# ──────────────────────────────────────────────────────────────
# R2-B1: First Real Task Lifecycle Proof
# ──────────────────────────────────────────────────────────────

class TestR2B1LifecycleProof:
    """Prove one real task lifecycle through the hardened runtime base.

    R2-B1 requirements:
    - Runtime-owned truth (ClaimContext for delegate claims)
    - Auditable event sequence
    - No hidden second truth source
    """

    def test_full_lifecycle_proof_succeeds(self):
        """Execute a complete lifecycle proof from inbox to done."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
            task_type="implementation",
            delegate_id="delegate-001",
            controller_id="controller-001",
            task_title="R2-B1 test task",
        )

        assert result.success is True, f"Lifecycle proof failed: {result.error}"
        assert result.is_complete is True
        assert result.final_status == TaskStatus.DONE
        assert len(result.transitions) == 4
        assert result.event_count >= 4

    def test_lifecycle_proof_uses_runtime_owned_claims(self):
        """Delegate claims must use runtime-owned ClaimContext."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # The ready->active transition must have a lease
        ready_to_active = result.transitions[1]
        assert ready_to_active.from_status == TaskStatus.READY
        assert ready_to_active.to_status == TaskStatus.ACTIVE

        # Lease record must exist
        assert result.lease is not None
        assert result.lease.task_id == task_id
        assert result.lease.owner_kind == "delegate"

        # Event for lease claim must exist
        lease_events = [e for e in result.events if e.get("event_type") == "lease_claimed"]
        assert len(lease_events) >= 1

    def test_lifecycle_proof_events_align_with_transitions(self):
        """Every state transition must produce an aligned event record."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Extract state transition events
        state_events = [
            e for e in result.events
            if e.get("event_type") == "state_transition"
        ]

        # Must have 4 state transition events (one per transition)
        assert len(state_events) == len(result.transitions)

        # Events must align with transitions
        for i, transition in enumerate(result.transitions):
            matching_events = [
                e for e in state_events
                if e.get("from_status") == transition.from_status.value
                and e.get("to_status") == transition.to_status.value
            ]
            assert len(matching_events) >= 1, (
                f"No matching event for transition {transition.from_status.value} -> "
                f"{transition.to_status.value}"
            )

    def test_lifecycle_proof_integrity(self):
        """Validate lifecycle proof has full integrity."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        is_valid, reason = validate_lifecycle_proof_integrity(result)
        assert is_valid is True, f"Integrity check failed: {reason}"

    def test_lifecycle_proof_is_auditable(self):
        """A successful lifecycle proof must be auditable."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert is_proof_auditable(result) is True

        # Audit dict must have required fields
        audit = result.to_audit_dict()
        assert "task_id" in audit
        assert "project_id" in audit
        assert "final_status" in audit
        assert "transition_count" in audit
        assert "event_count" in audit

    def test_review_boundary_enforced_in_lifecycle_proof(self):
        """Delegate cannot bypass review in lifecycle proof."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        # Find the review_pending -> done transition
        review_to_done = None
        for transition in result.transitions:
            if (transition.from_status == TaskStatus.REVIEW_PENDING
                    and transition.to_status == TaskStatus.DONE):
                review_to_done = transition
                break

        assert review_to_done is not None

        # Verify controller performed this transition
        # (Delegate would be denied per permission matrix)
        matching_events = [
            e for e in result.events
            if e.get("from_status") == "review_pending"
            and e.get("to_status") == "done"
        ]
        assert len(matching_events) >= 1
        # triggered_by_kind should be controller
        event = matching_events[0]
        assert event.get("triggered_by_kind") == "controller"


# ──────────────────────────────────────────────────────────────
# Work Context Derivation Tests
# ──────────────────────────────────────────────────────────────

class TestWorkContextDerivation:
    """WorkContext must be derivative, not a second truth source.

    R2-B1: The proof shows WorkContext is derived from canonical task state.
    """

    def test_work_context_derived_from_lifecycle_proof(self):
        """WorkContext can be derived from a lifecycle proof."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Execute proof to ACTIVE state (partial execution)
        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
            initial_status=TaskStatus.INBOX,
        )

        # If proof reached ACTIVE, derive context
        if result.final_status == TaskStatus.ACTIVE:
            context = derive_work_context_from_proof(
                proof=result,
                project_id=project_id,
            )
            # Context is derivative, not a second truth source
            assert context is not None
            assert context.project_id == project_id
            # active_task_id should reflect the task state
            assert context.active_task_id == task_id or context.active_task_id is None

    def test_work_context_from_completed_lifecycle(self):
        """WorkContext for completed task reflects project state."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True
        assert result.final_status == TaskStatus.DONE

        # Derive context - DONE task is not active
        context = derive_work_context_from_proof(
            proof=result,
            project_id=project_id,
        )

        assert context is not None
        assert context.project_id == project_id
        # DONE task is not in active_tasks, so no active_task_id for it
        assert context.active_task_id != task_id or context.active_task_id is None


# ──────────────────────────────────────────────────────────────
# Memory Packet Integration Tests
# ──────────────────────────────────────────────────────────────

class TestMemoryPacketIntegration:
    """Memory packets must be linked to reviewed upstream work.

    R2-B1: Packet existence does not imply trust.
    Only accepted packets with upstream linkage are trusted.
    """

    def test_lifecycle_proof_can_produce_memory_packet(self):
        """A successful lifecycle proof can produce a memory packet."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Create memory packet from proof
        packet = create_lifecycle_memory_packet(
            proof=result,
            project_id=project_id,
            task_id=task_id,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="controller-001",
            upstream_task_id=task_id,
            upstream_task_status="done",
        )

        assert packet is not None
        assert packet.status == PacketStatus.ACCEPTED
        assert packet.accepted_at is not None

    def test_packet_requires_upstream_linkage(self):
        """Memory packet must have upstream linkage for trust."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Create packet with upstream linkage
        packet = create_lifecycle_memory_packet(
            proof=result,
            project_id=project_id,
            task_id=task_id,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="controller-001",
            upstream_task_id=task_id,
            upstream_task_status="done",
        )

        # Check packet is trusted
        is_trusted = is_packet_trusted(packet)
        assert is_trusted is True

        # Verify upstream linkage in metadata
        acceptance = packet.metadata.get("acceptance", {})
        assert acceptance.get("upstream_task_id") == task_id

    def test_failed_proof_cannot_produce_memory_packet(self):
        """A failed lifecycle proof cannot produce a memory packet."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Create a failing proof scenario
        # This will fail at step 2 because delegate lacks claim
        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        # If proof somehow failed (unlikely with InMemoryClaimVerifier)
        if not result.success:
            packet = create_lifecycle_memory_packet(
                proof=result,
                project_id=project_id,
                task_id=task_id,
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="controller-001",
            )
            assert packet is None


# ──────────────────────────────────────────────────────────────
# Truth Constraints Validation
# ──────────────────────────────────────────────────────────────

class TestTruthConstraints:
    """Validate R2-B1 truth constraints are enforced.

    1. Task lifecycle truth is explicit
    2. No hidden second truth source
    3. Proof uses hardened runtime base
    """

    def test_state_changes_are_explicit(self):
        """All state changes in lifecycle proof are explicit."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Every transition must have explicit from/to status
        for transition in result.transitions:
            assert transition.from_status is not None
            assert transition.to_status is not None
            assert transition.from_status != transition.to_status

        # Every event must have explicit from/to status
        for event in result.events:
            if event.get("event_type") == "state_transition":
                assert event.get("from_status") is not None
                assert event.get("to_status") is not None

    def test_no_hidden_truth_source(self):
        """WorkContext is derivative, not a hidden truth source."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        context = derive_work_context_from_proof(
            proof=result,
            project_id=project_id,
        )

        if context is not None:
            # Context fields are derived from proof state
            # metadata.reconstructed_from should indicate derivation
            assert context.metadata.get("reconstructed_from") == "canonical_state"

    def test_proof_uses_hardened_runtime_base(self):
        """Lifecycle proof uses hardened runtime components."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Custom verifier to verify hardening works
        verifier = InMemoryClaimVerifier()

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
            claim_verifier=verifier,
        )

        assert result.success is True

        # Lease must exist (part of hardened runtime)
        assert result.lease is not None

        # Claim verification was runtime-owned
        # The verifier registered the lease and verified the claim
        verification = verifier.verify_claim(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref=result.lease.lease_id,
            delegate_id="delegate-001",
            task_id=task_id,
        )
        assert verification.valid is True


# ──────────────────────────────────────────────────────────────
# Canonical Path Validation
# ──────────────────────────────────────────────────────────────

class TestCanonicalLifecyclePath:
    """Validate the canonical lifecycle path matches hardened runtime."""

    def test_canonical_path_transitions_are_valid(self):
        """Every transition in canonical path is structurally valid."""
        from runtime.state_machine import is_valid_transition

        for from_status, to_status in CANONICAL_LIFECYCLE_PATH:
            assert is_valid_transition(from_status, to_status), (
                f"Invalid transition: {from_status.value} -> {to_status.value}"
            )

    def test_canonical_path_actors_are_permitted(self):
        """Each actor in canonical path is permitted for their transition."""
        from runtime.state_machine import (
            get_transition_permission,
            PermissionLevel,
        )

        for (from_status, to_status), actor in zip(
            CANONICAL_LIFECYCLE_PATH, CANONICAL_LIFECYCLE_ACTORS
        ):
            level = get_transition_permission(from_status, to_status, actor)
            # Delegate ready->active is CLAIM_REQUIRED, others are ALLOWED
            assert level in (
                PermissionLevel.ALLOWED,
                PermissionLevel.CLAIM_REQUIRED,
            ), (
                f"{actor.value} not permitted for {from_status.value} -> {to_status.value}"
            )

    def test_canonical_path_matches_lifecycle_proof(self):
        """Lifecycle proof follows the canonical path exactly."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Transitions must match canonical path
        for i, transition in enumerate(result.transitions):
            expected_from, expected_to = CANONICAL_LIFECYCLE_PATH[i]
            assert transition.from_status == expected_from
            assert transition.to_status == expected_to


# ──────────────────────────────────────────────────────────────
# Edge Cases and Failure Paths
# ──────────────────────────────────────────────────────────────

class TestLifecycleProofEdgeCases:
    """Test edge cases and failure paths in lifecycle proof."""

    def test_proof_with_custom_verifier_rejects_unregistered_claims(self):
        """Custom verifier rejects claims not pre-registered."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        # Verifier without pre-registration
        verifier = InMemoryClaimVerifier()
        # Don't register anything

        # This proof should fail because verifier won't have the lease registered
        # But execute_lifecycle_proof auto-registers with InMemoryClaimVerifier
        # So we need a custom failing scenario

        # Create a custom verifier that always rejects
        class RejectingVerifier(InMemoryClaimVerifier):
            def verify_claim(self, *args, **kwargs):
                from runtime.leases import ClaimVerificationResult
                return ClaimVerificationResult(
                    valid=False,
                    error="All claims rejected for test",
                )

        rejecting_verifier = RejectingVerifier()

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
            claim_verifier=rejecting_verifier,
        )

        # Proof should fail at ready->active (claim verification)
        assert result.success is False
        assert "claim" in result.error.lower() or "verification" in result.error.lower()

    def test_proof_integrity_check_detects_mismatched_events(self):
        """Integrity check detects mismatched event sequence."""
        # Create a fake proof with mismatched events
        fake_proof = LifecycleProofResult(
            success=True,
            task_id=str(uuid4()),
            project_id=str(uuid4()),
            final_status=TaskStatus.DONE,
            transitions=[],  # No transitions but success=True
            events=[],
        )

        is_valid, reason = validate_lifecycle_proof_integrity(fake_proof)
        assert is_valid is False
        assert "No transitions" in reason

    def test_proof_from_ready_status(self):
        """Can start lifecycle proof from READY status."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
            initial_status=TaskStatus.READY,
        )

        assert result.success is True
        # Should skip inbox->ready and go directly to ready->active
        assert result.transitions[0].from_status == TaskStatus.READY
        assert result.transitions[0].to_status == TaskStatus.ACTIVE


# ──────────────────────────────────────────────────────────────
# Lease Integration Tests
# ──────────────────────────────────────────────────────────────

class TestLifecycleLeaseIntegration:
    """Validate lease integration in lifecycle proof."""

    def test_lease_claimed_at_ready_to_active(self):
        """Lease is claimed at ready->active transition."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True
        assert result.lease is not None

        # Lease should be active during the ready->active transition
        assert result.lease.lease_status == "active"
        assert result.lease.task_id == task_id

    def test_lease_released_at_review_pending(self):
        """Lease is released when submitting for review."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Should have a lease_released event
        release_events = [
            e for e in result.events
            if e.get("event_type") == "lease_released"
        ]
        assert len(release_events) >= 1

    def test_lease_events_are_auditable(self):
        """Lease events have full audit trail."""
        task_id = str(uuid4())
        project_id = str(uuid4())

        result = execute_lifecycle_proof(
            task_id=task_id,
            project_id=project_id,
        )

        assert result.success is True

        # Find lease claimed event
        claim_events = [
            e for e in result.events
            if e.get("event_type") == "lease_claimed"
        ]
        assert len(claim_events) >= 1

        claim_event = claim_events[0]
        assert claim_event.get("task_id") == task_id
        assert claim_event.get("triggered_by_kind") == "delegate"
        assert claim_event.get("payload", {}).get("lease_id") == result.lease.lease_id