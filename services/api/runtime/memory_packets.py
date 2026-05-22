"""
IKE Runtime v0 – Memory Packets

Narrow trusted-snapshot metadata and acceptance helpers.
MemoryPacket is a compact recoverable summary, NOT a mutable truth source
or a broader memory engine.

Lifecycle: draft -> pending_review -> accepted
Trust rule: packet existence does NOT imply trust.
Only accepted packets are trusted for recall.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .state_machine import OwnerKind, UpstreamExistsFn


# ──────────────────────────────────────────────────────────────
# Packet Status
# ──────────────────────────────────────────────────────────────

class PacketStatus:
    """Memory packet lifecycle states.

    Packets are snapshots, not mutable living documents.
    draft -> pending_review -> accepted
    """
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"


VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    PacketStatus.DRAFT: {PacketStatus.PENDING_REVIEW},
    PacketStatus.PENDING_REVIEW: {PacketStatus.ACCEPTED},
    PacketStatus.ACCEPTED: set(),  # terminal – accepted packets are immutable
}


def is_valid_packet_transition(from_status: str, to_status: str) -> bool:
    """Check if a packet status transition is valid."""
    return to_status in VALID_STATUS_TRANSITIONS.get(from_status, set())


def get_valid_next_packet_statuses(current: str) -> set[str]:
    """Return valid next statuses for a packet."""
    return set(VALID_STATUS_TRANSITIONS.get(current, set()))


# ──────────────────────────────────────────────────────────────
# Packet Record
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MemoryPacket:
    """Compact recoverable runtime summary.

    Matches runtime_memory_packets table schema.

    Packets are immutable snapshots – once created, they should not
    be modified (except status progression toward accepted).

    Trust rule: packet existence does NOT imply trust.
    Only packets with status=accepted and accepted_at set are trusted.
    """
    memory_packet_id: str
    project_id: str
    task_id: str | None
    packet_type: str
    status: str
    acceptance_trigger: str | None
    title: str
    summary: str
    storage_ref: str | None
    content_hash: str | None
    parent_packet_id: str | None
    created_by_kind: str
    created_by_id: str
    created_at: str
    accepted_at: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_trusted(self) -> bool:
        """A packet is trusted only when accepted with a timestamp."""
        return self.status == PacketStatus.ACCEPTED and self.accepted_at is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for persistence."""
        return {
            "memory_packet_id": self.memory_packet_id,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "packet_type": self.packet_type,
            "status": self.status,
            "acceptance_trigger": self.acceptance_trigger,
            "title": self.title,
            "summary": self.summary,
            "storage_ref": self.storage_ref,
            "content_hash": self.content_hash,
            "parent_packet_id": self.parent_packet_id,
            "created_by_kind": self.created_by_kind,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at,
            "accepted_at": self.accepted_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryPacket":
        """Reconstruct from a persistence dict."""
        return cls(
            memory_packet_id=data["memory_packet_id"],
            project_id=data["project_id"],
            task_id=data.get("task_id"),
            packet_type=data["packet_type"],
            status=data["status"],
            acceptance_trigger=data.get("acceptance_trigger"),
            title=data["title"],
            summary=data.get("summary", ""),
            storage_ref=data.get("storage_ref"),
            content_hash=data.get("content_hash"),
            parent_packet_id=data.get("parent_packet_id"),
            created_by_kind=data["created_by_kind"],
            created_by_id=data["created_by_id"],
            created_at=data["created_at"],
            accepted_at=data.get("accepted_at"),
            metadata=data.get("metadata", {}),
        )


# ──────────────────────────────────────────────────────────────
# Packet Creation
# ──────────────────────────────────────────────────────────────

def create_packet(
    project_id: str,
    packet_type: str,
    title: str,
    summary: str,
    created_by_kind: OwnerKind,
    created_by_id: str,
    task_id: str | None = None,
    storage_ref: str | None = None,
    content_hash: str | None = None,
    parent_packet_id: str | None = None,
    acceptance_trigger: str | None = None,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> MemoryPacket:
    """Create a new draft memory packet.

    All packets start as DRAFT. Trust must be earned through
    explicit acceptance, not by creation.

    Args:
        project_id: The project this packet belongs to.
        packet_type: Type of packet (e.g., "study_result", "checkpoint").
        title: Human-readable title.
        summary: Compact summary content.
        created_by_kind: Who created the packet.
        created_by_id: Creator identifier.
        task_id: Optional associated task.
        storage_ref: Optional reference to object storage for heavy payload.
        content_hash: Optional content hash for integrity verification.
        parent_packet_id: Optional parent packet for versioning lineage.
        acceptance_trigger: Optional trigger that made this packet reviewable.
        metadata: Optional metadata dict.
        created_at: Optional explicit creation timestamp.

    Returns:
        New MemoryPacket in DRAFT status.
    """
    now = created_at or datetime.now(timezone.utc)
    return MemoryPacket(
        memory_packet_id=str(uuid4()),
        project_id=project_id,
        task_id=task_id,
        packet_type=packet_type,
        status=PacketStatus.DRAFT,
        acceptance_trigger=acceptance_trigger,
        title=title,
        summary=summary,
        storage_ref=storage_ref,
        content_hash=content_hash,
        parent_packet_id=parent_packet_id,
        created_by_kind=created_by_kind.value,
        created_by_id=created_by_id,
        created_at=now.isoformat(),
        accepted_at=None,
        metadata=metadata or {},
    )


# ──────────────────────────────────────────────────────────────
# Status Transition Helpers
# ──────────────────────────────────────────────────────────────

class PacketTransitionError(Exception):
    """Raised for invalid packet status transitions."""


def transition_to_review(
    packet: MemoryPacket,
    triggered_by_kind: OwnerKind,
    triggered_by_id: str,
    trigger_reason: str = "Packet submitted for review",
) -> dict[str, Any]:
    """Transition a draft packet to pending_review.

    Returns a dict of updates to apply to the database.
    The packet object itself is NOT mutated (immutability discipline).

    Raises:
        PacketTransitionError: If the packet is not in draft status.
    """
    if packet.status != PacketStatus.DRAFT:
        raise PacketTransitionError(
            f"Packet {packet.memory_packet_id} cannot transition to review: "
            f"current status is '{packet.status}', expected 'draft'."
        )
    if not triggered_by_id:
        raise PacketTransitionError(
            f"Packet {packet.memory_packet_id} cannot transition to review without "
            f"a non-empty triggered_by_id. Review submission provenance must record "
            f"the submitting actor id."
        )

    now = datetime.now(timezone.utc).isoformat()
    review_submission = {
        "submitted_by": triggered_by_kind.value,
        "submitted_by_id": triggered_by_id,
        "submitted_at": now,
        "reason": trigger_reason,
    }
    return {
        "memory_packet_id": packet.memory_packet_id,
        "status": PacketStatus.PENDING_REVIEW,
        "updated_at": now,
        "metadata": {
            **packet.metadata,
            "review_submitted_by": triggered_by_kind.value,
            "review_submitted_by_id": triggered_by_id,
            "review_submitted_at": now,
            "review_reason": trigger_reason,
            "review_submission": review_submission,
        },
    }


def accept_packet(
    packet: MemoryPacket,
    accepted_by_kind: OwnerKind,
    accepted_by_id: str,
    upstream_task_id: str | None = None,
    upstream_task_status: str | None = None,
    upstream_decision_id: str | None = None,
    acceptance_reason: str = "Packet accepted after review",
    verify_upstream_exists: UpstreamExistsFn | None = None,
) -> dict[str, Any]:
    """Accept a pending_review packet, linking it to reviewed upstream work.

    This is the trust gate. A packet can only be accepted if:
    1. It is in pending_review status.
    2. It is linked to reviewed upstream work (task closure, decision handoff,
       or explicit controller approval).
    3. (When verify_upstream_exists is provided) The referenced upstream object
       actually exists in Postgres – not just a linkage marker.

    R1-A5 ENFORCEMENT: The service layer SHOULD provide verify_upstream_exists.
    Calling accept_packet without a verifier is allowed for backward compatibility,
    but produces packets with weaker trust guarantees. Packets accepted without
    upstream verification should be flagged for later audit.

    Returns a dict of updates to apply to the database.
    The packet object itself is NOT mutated (immutability discipline).

    Args:
        packet: The packet to accept (must be in pending_review status).
        accepted_by_kind: Role accepting the packet.
        accepted_by_id: Accepting actor's identifier.
        upstream_task_id: Optional linked task that was reviewed and accepted.
        upstream_task_status: Optional status of the linked task.
        upstream_decision_id: Optional linked decision for handoff context.
        acceptance_reason: Reason for acceptance.
        verify_upstream_exists: Callback to verify that referenced upstream
            objects actually exist in Postgres. Signature:
            (object_type: str, object_id: str) -> bool.
            R1-A5: SHOULD be provided by the service layer. When omitted,
            the packet is accepted with weaker trust guarantees.

    Raises:
        PacketTransitionError: If the packet is not in pending_review status,
            or if upstream existence verification fails.
    """
    if packet.status != PacketStatus.PENDING_REVIEW:
        raise PacketTransitionError(
            f"Packet {packet.memory_packet_id} cannot be accepted: "
            f"current status is '{packet.status}', expected 'pending_review'. "
            f"Accepted packets must be in pending_review status first."
        )

    # Guardrail: a delegate cannot accept their own packet.
    # Packet existence does not imply trust – acceptance requires a different
    # actor with review authority.
    if (accepted_by_kind.value == packet.created_by_kind
            and accepted_by_id == packet.created_by_id):
        raise PacketTransitionError(
            f"Packet {packet.memory_packet_id} cannot be self-accepted: "
            f"created by {packet.created_by_kind}:{packet.created_by_id}, "
            f"acceptance by same actor is not permitted. "
            f"A separate reviewer or controller must accept the packet."
        )

    now = datetime.now(timezone.utc).isoformat()

    # FIX: Explicit upstream linkage is REQUIRED for trust promotion.
    # At least one of upstream_task_id or upstream_decision_id must be
    # provided. Acceptance without reviewed upstream linkage is rejected.
    if upstream_task_id is None and upstream_decision_id is None:
        raise PacketTransitionError(
            f"Packet {packet.memory_packet_id} cannot be accepted without "
            f"explicit upstream linkage. Provide upstream_task_id (for task "
            f"closure) or upstream_decision_id (for decision handoff). "
            f"Accepted packets must be auditably tied to reviewed upstream work."
        )

    # R1-A1 HARDENING: Verify upstream object existence in Postgres.
    # Linkage presence alone is not enough – the referenced object must
    # actually exist. This prevents fake linkage markers from passing
    # the trust boundary.
    if verify_upstream_exists is not None:
        if upstream_task_id is not None:
            if not verify_upstream_exists("task", upstream_task_id):
                raise PacketTransitionError(
                    f"Packet {packet.memory_packet_id} cannot be accepted: "
                    f"referenced upstream task '{upstream_task_id}' does not "
                    f"exist in Postgres. Linkage must reference a real object."
                )
        if upstream_decision_id is not None:
            if not verify_upstream_exists("decision", upstream_decision_id):
                raise PacketTransitionError(
                    f"Packet {packet.memory_packet_id} cannot be accepted: "
                    f"referenced upstream decision '{upstream_decision_id}' does "
                    f"not exist in Postgres. Linkage must reference a real object."
                )

    # Build acceptance linkage metadata
    linkage: dict[str, Any] = {
        "accepted_by": accepted_by_kind.value,
        "accepted_by_id": accepted_by_id,
        "accepted_at": now,
        "acceptance_reason": acceptance_reason,
    }

    # Always record upstream linkage
    if upstream_task_id:
        linkage["upstream_task_id"] = upstream_task_id
    if upstream_task_status:
        linkage["upstream_task_status"] = upstream_task_status
    if upstream_decision_id:
        linkage["upstream_decision_id"] = upstream_decision_id

    return {
        "memory_packet_id": packet.memory_packet_id,
        "status": PacketStatus.ACCEPTED,
        "accepted_at": now,
        "updated_at": now,
        "metadata": {
            **packet.metadata,
            "acceptance": linkage,
        },
    }


# ──────────────────────────────────────────────────────────────
# Trust Boundary Checks
# ──────────────────────────────────────────────────────────────

def is_packet_trusted(
    packet: MemoryPacket,
    verify_upstream_exists: UpstreamExistsFn | None = None,
) -> bool:
    """Check if a packet is trusted for recall.

    Trust requires:
    1. Status is 'accepted'.
    2. accepted_at timestamp is set.
    3. Metadata contains acceptance linkage with accepted_by.
    4. Metadata contains explicit upstream linkage
       (upstream_task_id or upstream_decision_id).
    5. (When verify_upstream_exists is provided) The referenced upstream
       object actually exists in Postgres – preventing fake linkage from
       passing the trust boundary.
    """
    if not packet.is_trusted:
        return False

    # Verify acceptance linkage exists
    acceptance = packet.metadata.get("acceptance", {})
    if not acceptance:
        return False

    # Must have an accepting actor
    if not acceptance.get("accepted_by"):
        return False

    # FIX: Must have explicit upstream linkage
    has_upstream_linkage = (
        acceptance.get("upstream_task_id") is not None
        or acceptance.get("upstream_decision_id") is not None
    )
    if not has_upstream_linkage:
        return False

    # R1-A1 HARDENING: Verify upstream object existence if verifier provided.
    # This is the runtime-layer trust gate: linkage presence is necessary
    # but not sufficient – the referenced object must exist in Postgres.
    if verify_upstream_exists is not None:
        upstream_task_id = acceptance.get("upstream_task_id")
        upstream_decision_id = acceptance.get("upstream_decision_id")
        if upstream_task_id is not None:
            if not verify_upstream_exists("task", upstream_task_id):
                return False
        if upstream_decision_id is not None:
            if not verify_upstream_exists("decision", upstream_decision_id):
                return False

    return True


def get_trusted_packets(
    packets: list[MemoryPacket],
    verify_upstream_exists: UpstreamExistsFn | None = None,
) -> list[MemoryPacket]:
    """Filter a list of packets to only trusted ones.

    This is the recall-path gate: only trusted packets are
    returned for downstream memory recall.

    Args:
        packets: List of packets to filter.
        verify_upstream_exists: Optional upstream existence verifier.
            When provided, packets with fake/missing upstream references
            are excluded from trusted recall.
    """
    return [p for p in packets if is_packet_trusted(p, verify_upstream_exists)]


def validate_packet_trust_boundary(
    packet: MemoryPacket,
    verify_upstream_exists: UpstreamExistsFn | None = None,
) -> tuple[bool, str]:
    """Validate the trust boundary for a packet.

    Returns:
        (is_trusted, reason) tuple explaining the trust status.

    Args:
        packet: The packet to validate.
        verify_upstream_exists: Optional upstream existence verifier.
            When provided, trust requires the referenced upstream object
            to actually exist in Postgres.
    """
    if packet.status != PacketStatus.ACCEPTED:
        return False, f"Packet status is '{packet.status}', not 'accepted'"

    if packet.accepted_at is None:
        return False, "Packet has no accepted_at timestamp"

    acceptance = packet.metadata.get("acceptance", {})
    if not acceptance:
        return False, "Packet has no acceptance linkage metadata"

    accepted_by = acceptance.get("accepted_by")
    if not accepted_by:
        return False, "Packet acceptance has no accepted_by field"

    # FIX: Must have explicit upstream linkage
    has_upstream_linkage = (
        acceptance.get("upstream_task_id") is not None
        or acceptance.get("upstream_decision_id") is not None
    )
    if not has_upstream_linkage:
        return False, (
            "Packet has no explicit upstream linkage. "
            "Accepted packets must have upstream_task_id or upstream_decision_id."
        )

    # R1-A1 HARDENING: Verify upstream object existence if verifier provided.
    if verify_upstream_exists is not None:
        upstream_task_id = acceptance.get("upstream_task_id")
        upstream_decision_id = acceptance.get("upstream_decision_id")
        if upstream_task_id is not None:
            if not verify_upstream_exists("task", upstream_task_id):
                return False, (
                    f"Referenced upstream task '{upstream_task_id}' does not "
                    f"exist in Postgres. Fake linkage markers cannot pass trust."
                )
        if upstream_decision_id is not None:
            if not verify_upstream_exists("decision", upstream_decision_id):
                return False, (
                    f"Referenced upstream decision '{upstream_decision_id}' does "
                    f"not exist in Postgres. Fake linkage markers cannot pass trust."
                )

    return True, "Packet is trusted with valid acceptance linkage and upstream reference"


# ──────────────────────────────────────────────────────────────
# Packet Deletion (Soft)
# ──────────────────────────────────────────────────────────────

def soft_delete_packet(
    packet: MemoryPacket,
    reason: str = "Packet soft-deleted",
) -> dict[str, Any]:
    """Soft-delete a non-accepted packet.

    Accepted packets should NOT be deleted – they are part of the
    trust chain. Only draft and pending_review packets can be soft-deleted.

    Returns a dict of updates to apply to the database.

    Raises:
        PacketTransitionError: If attempting to delete an accepted packet.
    """
    if packet.status == PacketStatus.ACCEPTED:
        raise PacketTransitionError(
            f"Cannot soft-delete accepted packet {packet.memory_packet_id}. "
            f"Accepted packets are part of the trust chain and must not be removed."
        )

    now = datetime.now(timezone.utc).isoformat()
    return {
        "memory_packet_id": packet.memory_packet_id,
        "status": PacketStatus.DRAFT,
        "updated_at": now,
        "metadata": {
            **packet.metadata,
            "deleted": True,
            "deleted_at": now,
            "deleted_reason": reason,
        },
    }
