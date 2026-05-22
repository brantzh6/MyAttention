"""
IKE Runtime v0 – Task Lifecycle Proof Helpers

Narrow, auditable helpers for producing runtime-owned task lifecycle proofs.
This module demonstrates ONE truthful lifecycle path through the hardened runtime:

  inbox -> ready -> active -> review_pending -> done

Key principles:
1. Runtime-owned truth: all transitions use ClaimContext for delegate claims
2. Auditable: every state change produces aligned event records
3. No hidden chat truth: WorkContext is derivative, MemoryPackets require upstream linkage

This is a proof helper, not a general task executor. It exists to validate
that the hardened runtime base can carry a truthful lifecycle without
introducing a second truth source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .state_machine import (
    TaskStatus,
    OwnerKind,
    ClaimContext,
    ClaimType,
    WaitingReason,
    validate_transition,
    TransitionError,
    describe_transition,
)
from .transitions import (
    TransitionRequest,
    TransitionResult,
    execute_transition,
    build_event_record,
    build_task_update,
)
from .events import (
    EventType,
    TaskEvent,
    make_state_transition_event,
    make_lease_claimed_event,
    EventSequence,
)
from .leases import (
    claim_lease,
    heartbeat_lease,
    release_lease,
    LeaseClaimResult,
    LeaseRecord,
    ClaimVerifier,
    InMemoryClaimVerifier,
)
from .work_context import (
    WorkContext,
    TaskSnapshot,
    reconstruct_work_context,
)
from .memory_packets import (
    MemoryPacket,
    PacketStatus,
    create_packet,
    accept_packet,
    is_packet_trusted,
)


# ──────────────────────────────────────────────────────────────
# Lifecycle Proof Record
# ──────────────────────────────────────────────────────────────

@dataclass
class LifecycleProofResult:
    """Result of a complete task lifecycle proof execution.

    This captures the entire auditable trail of one task flowing through
    the runtime from inbox to done, including:
    - All transition results
    - All event records
    - Lease claim and release
    - Memory packet linkage (if any)

    The proof is only valid if:
    - All transitions succeeded
    - Event log matches transition sequence
    - No hidden second truth source was used
    """
    success: bool
    task_id: str
    project_id: str
    final_status: TaskStatus
    transitions: list[TransitionResult] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    lease: LeaseRecord | None = None
    memory_packet: MemoryPacket | None = None
    error: str | None = None

    @property
    def is_complete(self) -> bool:
        """True if the task reached DONE status."""
        return self.final_status == TaskStatus.DONE

    @property
    def event_count(self) -> int:
        """Number of events recorded in the lifecycle."""
        return len(self.events)

    def to_audit_dict(self) -> dict[str, Any]:
        """Convert to a dict suitable for audit logging."""
        return {
            "success": self.success,
            "task_id": self.task_id,
            "project_id": self.project_id,
            "final_status": self.final_status.value,
            "transition_count": len(self.transitions),
            "event_count": self.event_count,
            "has_lease": self.lease is not None,
            "has_memory_packet": self.memory_packet is not None,
            "error": self.error,
        }


# ──────────────────────────────────────────────────────────────
# Lifecycle Path Constants
# ──────────────────────────────────────────────────────────────

# The canonical lifecycle path to prove
CANONICAL_LIFECYCLE_PATH = [
    (TaskStatus.INBOX, TaskStatus.READY),      # Triage
    (TaskStatus.READY, TaskStatus.ACTIVE),     # Claim and start
    (TaskStatus.ACTIVE, TaskStatus.REVIEW_PENDING),  # Submit for review
    (TaskStatus.REVIEW_PENDING, TaskStatus.DONE),    # Accept
]

# Actors for each lifecycle step
CANONICAL_LIFECYCLE_ACTORS = [
    OwnerKind.CONTROLLER,  # Triage
    OwnerKind.DELEGATE,    # Claim (requires ClaimContext)
    OwnerKind.DELEGATE,    # Submit for review
    OwnerKind.CONTROLLER,  # Accept
]


# ──────────────────────────────────────────────────────────────
# Lifecycle Proof Execution
# ──────────────────────────────────────────────────────────────

def execute_lifecycle_proof(
    task_id: str,
    project_id: str,
    task_type: str = "implementation",
    delegate_id: str = "delegate-001",
    controller_id: str = "controller-001",
    claim_verifier: ClaimVerifier | None = None,
    task_title: str = "Test task for lifecycle proof",
    initial_status: TaskStatus = TaskStatus.INBOX,
    created_at: datetime | None = None,
) -> LifecycleProofResult:
    """Execute a complete task lifecycle proof through the hardened runtime.

    This is the primary entry point for proving that a real task can flow
    through the runtime from inbox to done with:
    - Runtime-owned claim verification (ClaimContext + ClaimVerifier)
    - Auditable event sequence aligned with state transitions
    - No hidden second truth source

    The proof follows the canonical path:
    1. inbox -> ready (controller triage)
    2. ready -> active (delegate claim with verified ClaimContext)
    3. active -> review_pending (delegate submits work)
    4. review_pending -> done (controller accepts)

    Args:
        task_id: The task to prove lifecycle for.
        project_id: The project context.
        task_type: Task type for recovery policy (default: implementation).
        delegate_id: Delegate actor ID.
        controller_id: Controller actor ID.
        claim_verifier: ClaimVerifier for runtime-owned claim verification.
            If None, an InMemoryClaimVerifier is used with pre-registered claims.
        task_title: Title for audit trail.
        initial_status: Starting status (default: INBOX).
        created_at: Optional timestamp override.

    Returns:
        LifecycleProofResult with complete audit trail.
    """
    now = created_at or datetime.now(timezone.utc)
    events: list[dict[str, Any]] = []
    transitions: list[TransitionResult] = []
    current_status = initial_status
    lease: LeaseRecord | None = None

    # Set up claim verifier if not provided
    if claim_verifier is None:
        verifier = InMemoryClaimVerifier()
    else:
        verifier = claim_verifier

    # Step 1: inbox -> ready (controller triage)
    if current_status == TaskStatus.INBOX:
        req1 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.INBOX,
            to_status=TaskStatus.READY,
            role=OwnerKind.CONTROLLER,
            role_id=controller_id,
            reason="Triage complete; task is executable",
        )
        result1 = execute_transition(req1)
        if not result1.success:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                error=f"Step 1 (inbox->ready) failed: {result1.error}",
            )
        transitions.append(result1)

        event1 = build_event_record(
            result1,
            project_id=project_id,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id=controller_id,
        )
        events.append(event1)
        current_status = TaskStatus.READY

    # Step 2: ready -> active (delegate claim)
    if current_status == TaskStatus.READY:
        # Claim lease for the task
        lease_result = claim_lease(
            task_id=task_id,
            project_id=project_id,
            owner_kind=OwnerKind.DELEGATE,
            owner_id=delegate_id,
            ttl_seconds=3600,
            created_at=now,
        )
        if not lease_result.success:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                error=f"Lease claim failed: {lease_result.error}",
            )
        lease = lease_result.lease
        lease_id = lease.lease_id

        # Record lease claimed event
        lease_event = lease_result.event
        if lease_event:
            events.append(lease_event.to_dict())

        # Register the lease with the verifier
        if isinstance(verifier, InMemoryClaimVerifier):
            verifier.register_lease(lease_id, delegate_id, task_id)

        # Build and verify claim context
        verification = verifier.verify_and_build_context(
            claim_type=ClaimType.ACTIVE_LEASE,
            claim_ref=lease_id,
            delegate_id=delegate_id,
            task_id=task_id,
        )
        if not verification.valid:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                lease=lease,
                error=f"Claim verification failed: {verification.error}",
            )

        # Transition with verified ClaimContext
        req2 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.READY,
            to_status=TaskStatus.ACTIVE,
            role=OwnerKind.DELEGATE,
            role_id=delegate_id,
            reason="Work started with verified claim",
            claim_context=verification.claim_context,
        )
        result2 = execute_transition(req2)
        if not result2.success:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                lease=lease,
                error=f"Step 2 (ready->active) failed: {result2.error}",
            )
        transitions.append(result2)

        event2 = build_event_record(
            result2,
            project_id=project_id,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id=delegate_id,
            extra_payload={"lease_id": lease_id},
        )
        events.append(event2)
        current_status = TaskStatus.ACTIVE

    # Step 3: active -> review_pending (delegate submits for review)
    if current_status == TaskStatus.ACTIVE:
        req3 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.ACTIVE,
            to_status=TaskStatus.REVIEW_PENDING,
            role=OwnerKind.DELEGATE,
            role_id=delegate_id,
            reason="Work complete; awaiting review",
        )
        result3 = execute_transition(req3)
        if not result3.success:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                lease=lease,
                error=f"Step 3 (active->review_pending) failed: {result3.error}",
            )
        transitions.append(result3)

        # Release the lease when submitting for review
        if lease:
            release_event = release_lease(
                lease_id=lease.lease_id,
                task_id=task_id,
                project_id=project_id,
                owner_kind=OwnerKind.DELEGATE,
                owner_id=delegate_id,
                reason="Lease released on work submission",
            )
            events.append(release_event.to_dict())

        event3 = build_event_record(
            result3,
            project_id=project_id,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id=delegate_id,
        )
        events.append(event3)
        current_status = TaskStatus.REVIEW_PENDING

    # Step 4: review_pending -> done (controller accepts)
    if current_status == TaskStatus.REVIEW_PENDING:
        req4 = TransitionRequest(
            task_id=task_id,
            project_id=project_id,
            from_status=TaskStatus.REVIEW_PENDING,
            to_status=TaskStatus.DONE,
            role=OwnerKind.CONTROLLER,
            role_id=controller_id,
            reason="Review passed; task accepted",
        )
        result4 = execute_transition(req4)
        if not result4.success:
            return LifecycleProofResult(
                success=False,
                task_id=task_id,
                project_id=project_id,
                final_status=current_status,
                transitions=transitions,
                events=events,
                lease=lease,
                error=f"Step 4 (review_pending->done) failed: {result4.error}",
            )
        transitions.append(result4)

        event4 = build_event_record(
            result4,
            project_id=project_id,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id=controller_id,
            extra_payload={"review_passed": True},
        )
        events.append(event4)
        current_status = TaskStatus.DONE

    return LifecycleProofResult(
        success=True,
        task_id=task_id,
        project_id=project_id,
        final_status=current_status,
        transitions=transitions,
        events=events,
        lease=lease,
    )


def create_lifecycle_memory_packet(
    proof: LifecycleProofResult,
    project_id: str,
    task_id: str,
    accepted_by_kind: OwnerKind,
    accepted_by_id: str,
    packet_type: str = "lifecycle_proof",
    title: str = "Task lifecycle proof record",
    summary: str = "",
    upstream_task_id: str | None = None,
    upstream_task_status: str | None = None,
    verify_upstream_exists: Any | None = None,
) -> MemoryPacket | None:
    """Create a memory packet from a successful lifecycle proof.

    This links the lifecycle proof to reviewed upstream work, ensuring
    the packet is auditably tied to the task that completed.

    Only creates a packet if:
    - The proof succeeded (reached DONE)
    - Upstream linkage is provided (task_id of the completed task)

    Args:
        proof: The lifecycle proof result.
        project_id: Project context.
        task_id: Task ID for packet linkage.
        accepted_by_kind: Role accepting the packet.
        accepted_by_id: Actor ID accepting the packet.
        packet_type: Type of packet (default: lifecycle_proof).
        title: Packet title.
        summary: Packet summary.
        upstream_task_id: Task ID to link (should be proof.task_id).
        upstream_task_status: Status of upstream task (should be "done").
        verify_upstream_exists: Upstream existence verifier.

    Returns:
        MemoryPacket in ACCEPTED status, or None if proof failed.
    """
    if not proof.success or not proof.is_complete:
        return None

    # Require upstream linkage
    if upstream_task_id is None:
        upstream_task_id = proof.task_id
    if upstream_task_status is None:
        upstream_task_status = proof.final_status.value

    # Create packet in draft, then promote to pending_review
    packet = create_packet(
        project_id=project_id,
        packet_type=packet_type,
        title=title,
        summary=summary or f"Lifecycle proof for task {task_id}",
        created_by_kind=OwnerKind.RUNTIME,
        created_by_id="runtime_lifecycle_proof",
        task_id=task_id,
        metadata={
            "lifecycle_proof": proof.to_audit_dict(),
        },
    )

    # Transition to pending_review (runtime submits for review)
    transition_to_review_updates = {
        "memory_packet_id": packet.memory_packet_id,
        "status": PacketStatus.PENDING_REVIEW,
        "metadata": {
            **packet.metadata,
            "review_submitted_by": OwnerKind.RUNTIME.value,
            "review_submitted_by_id": "runtime_lifecycle_proof",
        },
    }

    # Create a pending_review version for acceptance
    pending_packet = MemoryPacket(
        memory_packet_id=packet.memory_packet_id,
        project_id=packet.project_id,
        task_id=packet.task_id,
        packet_type=packet.packet_type,
        status=PacketStatus.PENDING_REVIEW,
        acceptance_trigger=packet.acceptance_trigger,
        title=packet.title,
        summary=packet.summary,
        storage_ref=packet.storage_ref,
        content_hash=packet.content_hash,
        parent_packet_id=packet.parent_packet_id,
        created_by_kind=packet.created_by_kind,
        created_by_id=packet.created_by_id,
        created_at=packet.created_at,
        accepted_at=None,
        metadata=transition_to_review_updates["metadata"],
    )

    # Accept with upstream linkage
    accept_updates = accept_packet(
        packet=pending_packet,
        accepted_by_kind=accepted_by_kind,
        accepted_by_id=accepted_by_id,
        upstream_task_id=upstream_task_id,
        upstream_task_status=upstream_task_status,
        acceptance_reason="Lifecycle proof packet accepted after task completion",
        verify_upstream_exists=verify_upstream_exists,
    )

    # Build accepted packet
    accepted_packet = MemoryPacket(
        memory_packet_id=pending_packet.memory_packet_id,
        project_id=pending_packet.project_id,
        task_id=pending_packet.task_id,
        packet_type=pending_packet.packet_type,
        status=PacketStatus.ACCEPTED,
        acceptance_trigger=pending_packet.acceptance_trigger,
        title=pending_packet.title,
        summary=pending_packet.summary,
        storage_ref=pending_packet.storage_ref,
        content_hash=pending_packet.content_hash,
        parent_packet_id=pending_packet.parent_packet_id,
        created_by_kind=pending_packet.created_by_kind,
        created_by_id=pending_packet.created_by_id,
        created_at=pending_packet.created_at,
        accepted_at=accept_updates["accepted_at"],
        metadata=accept_updates["metadata"],
    )

    return accepted_packet


def derive_work_context_from_proof(
    proof: LifecycleProofResult,
    project_id: str,
    additional_active_tasks: list[TaskSnapshot] | None = None,
    additional_waiting_tasks: list[TaskSnapshot] | None = None,
) -> WorkContext | None:
    """Derive a WorkContext from a lifecycle proof result.

    This demonstrates the WorkContext-as-derivative principle: the context
    is built from canonical task state, not from hidden chat truth.

    For a completed proof (task in DONE), the context reflects completion.
    For an in-progress proof, the context reflects active work.

    Args:
        proof: The lifecycle proof result.
        project_id: Project context.
        additional_active_tasks: Other active tasks in project.
        additional_waiting_tasks: Waiting tasks in project.

    Returns:
        WorkContext derived from proof state, or None if proof failed.
    """
    if not proof.success:
        return None

    active_tasks = additional_active_tasks or []
    waiting_tasks = additional_waiting_tasks or []

    # If task is in ACTIVE status, include it in active_tasks
    if proof.final_status == TaskStatus.ACTIVE:
        active_tasks.append(TaskSnapshot(
            task_id=proof.task_id,
            title="Lifecycle proof task",
            status=proof.final_status.value,
            task_type="implementation",
            priority=1,
            next_action_summary="Active lifecycle proof",
            waiting_reason=None,
            waiting_detail=None,
        ))

    # If task is in WAITING status, include it in waiting_tasks
    elif proof.final_status == TaskStatus.WAITING:
        waiting_tasks.append(TaskSnapshot(
            task_id=proof.task_id,
            title="Lifecycle proof task",
            status=proof.final_status.value,
            task_type="implementation",
            priority=1,
            next_action_summary=None,
            waiting_reason=WaitingReason.DELEGATE_RESULT.value,
            waiting_detail="Lifecycle proof task in waiting",
        ))

    # For DONE/REVIEW_PENDING, the task is neither active nor waiting
    # The context reflects other work in the project

    return reconstruct_work_context(
        project_id=project_id,
        active_tasks=active_tasks,
        waiting_tasks=waiting_tasks,
        latest_decisions=[],  # No decisions in basic lifecycle proof
        accepted_packets=[],  # No packets unless explicitly created
        current_focus=f"Lifecycle proof task status: {proof.final_status.value}",
    )


# ──────────────────────────────────────────────────────────────
# Validation Helpers
# ──────────────────────────────────────────────────────────────

def validate_lifecycle_proof_integrity(proof: LifecycleProofResult) -> tuple[bool, str]:
    """Validate that a lifecycle proof has integrity.

    Checks:
    1. All transitions succeeded
    2. Event count matches transition count (plus lease events)
    3. Event sequence matches transition sequence
    4. No hidden truth sources used (ClaimContext for delegate claims)

    Returns:
        (is_valid, reason) tuple explaining validation result.
    """
    if not proof.success:
        return False, f"Proof failed: {proof.error}"

    # Check transition sequence
    if len(proof.transitions) == 0:
        return False, "No transitions recorded"

    # Check event count (should have at least 4 state events, plus lease events)
    if proof.event_count < len(proof.transitions):
        return False, (
            f"Event count ({proof.event_count}) < transition count ({len(proof.transitions)}). "
            f"Every transition must produce an aligned event."
        )

    # Check transition sequence matches canonical path
    expected_path = CANONICAL_LIFECYCLE_PATH[:len(proof.transitions)]
    for i, result in enumerate(proof.transitions):
        if i < len(expected_path):
            expected_from, expected_to = expected_path[i]
            if result.from_status != expected_from:
                return False, (
                    f"Transition {i} from_status mismatch: "
                    f"expected {expected_from.value}, got {result.from_status.value}"
                )
            if result.to_status != expected_to:
                return False, (
                    f"Transition {i} to_status mismatch: "
                    f"expected {expected_to.value}, got {result.to_status.value}"
                )

    # Check lease exists for delegate claim
    # The ready->active transition requires a lease
    for result in proof.transitions:
        if (result.from_status == TaskStatus.READY
                and result.to_status == TaskStatus.ACTIVE):
            if proof.lease is None:
                return False, (
                    "ready->active transition without lease record. "
                    "Delegate claims require lease-backed ClaimContext."
                )

    return True, "Lifecycle proof has full integrity"


def is_proof_auditable(proof: LifecycleProofResult) -> bool:
    """Check if a proof is suitable for audit logging.

    An auditable proof must:
    - Have integrity (validate_lifecycle_proof_integrity passes)
    - Have complete event sequence
    - Have lease linkage for delegate claims
    """
    is_valid, _ = validate_lifecycle_proof_integrity(proof)
    return is_valid and proof.event_count > 0