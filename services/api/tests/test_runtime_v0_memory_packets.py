"""
Tests for IKE Runtime v0 memory packets.

Validates:
- draft -> pending_review -> accepted lifecycle
- Explicit accepted-upstream linkage
- Packet presence alone not implying trust
- Trust-boundary proof:
  - delegate-created packet cannot self-promote to accepted
  - non-accepted packet excluded from trusted recall
  - explicit reviewed upstream linkage required for trust
- R1-A1 Hardening – Upstream Existence Verification:
  - trusted memory with real upstream object passes
  - trusted memory with fake/missing upstream object fails
  - acceptance rejected when upstream object doesn't exist
  - verifier callback pattern for Postgres-backed verification
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from runtime.state_machine import OwnerKind
from runtime.memory_packets import (
    PacketStatus,
    MemoryPacket,
    is_valid_packet_transition,
    get_valid_next_packet_statuses,
    create_packet,
    PacketTransitionError,
    transition_to_review,
    accept_packet,
    is_packet_trusted,
    get_trusted_packets,
    validate_packet_trust_boundary,
    soft_delete_packet,
)


# ──────────────────────────────────────────────────────────────
# Packet Status Enum
# ──────────────────────────────────────────────────────────────

class TestPacketStatus:
    def test_three_statuses(self):
        assert PacketStatus.DRAFT == "draft"
        assert PacketStatus.PENDING_REVIEW == "pending_review"
        assert PacketStatus.ACCEPTED == "accepted"

    def test_valid_transitions(self):
        assert is_valid_packet_transition("draft", "pending_review") is True
        assert is_valid_packet_transition("pending_review", "accepted") is True

    def test_no_backward_transitions(self):
        assert is_valid_packet_transition("pending_review", "draft") is False
        assert is_valid_packet_transition("accepted", "pending_review") is False
        assert is_valid_packet_transition("accepted", "draft") is False

    def test_no_skip(self):
        """Cannot skip from draft directly to accepted."""
        assert is_valid_packet_transition("draft", "accepted") is False

    def test_self_transition_invalid(self):
        assert is_valid_packet_transition("draft", "draft") is False
        assert is_valid_packet_transition("accepted", "accepted") is False

    def test_unknown_status_invalid(self):
        assert is_valid_packet_transition("unknown", "draft") is False

    def test_next_statuses_from_draft(self):
        assert get_valid_next_packet_statuses("draft") == {"pending_review"}

    def test_next_statuses_from_pending_review(self):
        assert get_valid_next_packet_statuses("pending_review") == {"accepted"}

    def test_next_statuses_from_accepted(self):
        assert get_valid_next_packet_statuses("accepted") == set()

    def test_next_statuses_from_unknown(self):
        assert get_valid_next_packet_statuses("unknown") == set()


# ──────────────────────────────────────────────────────────────
# MemoryPacket Dataclass
# ──────────────────────────────────────────────────────────────

class TestMemoryPacketDataclass:
    def test_create_draft_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Research findings",
            summary="Key insights about X",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        assert pkt.status == PacketStatus.DRAFT
        assert pkt.accepted_at is None
        assert pkt.is_trusted is False
        assert pkt.memory_packet_id is not None

    def test_packet_is_frozen(self):
        """MemoryPacket must be immutable."""
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        with pytest.raises(AttributeError):
            pkt.status = "accepted"

    def test_to_dict_matches_schema(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="checkpoint",
            title="Checkpoint 1",
            summary="Step 1 complete",
            created_by_kind=OwnerKind.RUNTIME,
            created_by_id="runtime",
            storage_ref="s3://bucket/key",
            content_hash="abc123",
        )
        d = pkt.to_dict()
        assert d["memory_packet_id"] == pkt.memory_packet_id
        assert d["project_id"] == "proj-1"
        assert d["packet_type"] == "checkpoint"
        assert d["status"] == "draft"
        assert d["storage_ref"] == "s3://bucket/key"
        assert d["content_hash"] == "abc123"
        assert d["accepted_at"] is None

    def test_from_dict_roundtrip(self):
        original = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
            task_id="task-1",
        )
        restored = MemoryPacket.from_dict(original.to_dict())
        assert restored.memory_packet_id == original.memory_packet_id
        assert restored.status == original.status
        assert restored.task_id == original.task_id

    def test_packet_with_optional_fields(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="checkpoint",
            title="Checkpoint",
            summary="Done",
            created_by_kind=OwnerKind.RUNTIME,
            created_by_id="runtime",
            task_id="task-1",
            storage_ref="s3://bucket/file",
            content_hash="sha256:abc",
            parent_packet_id="parent-1",
            acceptance_trigger="task_done",
            metadata={"version": 2},
        )
        assert pkt.task_id == "task-1"
        assert pkt.storage_ref == "s3://bucket/file"
        assert pkt.content_hash == "sha256:abc"
        assert pkt.parent_packet_id == "parent-1"
        assert pkt.acceptance_trigger == "task_done"
        assert pkt.metadata["version"] == 2

    def test_packet_has_no_trust_by_default(self):
        """Draft packets are never trusted."""
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
        )
        assert pkt.is_trusted is False


# ──────────────────────────────────────────────────────────────
# Transition to Review
# ──────────────────────────────────────────────────────────────

class TestTransitionToReview:
    def test_draft_to_review(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        updates = transition_to_review(
            pkt,
            triggered_by_kind=OwnerKind.DELEGATE,
            triggered_by_id="del-001",
            trigger_reason="Study complete",
        )
        assert updates["status"] == PacketStatus.PENDING_REVIEW
        assert updates["metadata"]["review_submitted_by"] == "delegate"
        assert updates["metadata"]["review_submitted_by_id"] == "del-001"
        assert "review_submitted_at" in updates["metadata"]
        assert updates["metadata"]["review_reason"] == "Study complete"
        submission = updates["metadata"]["review_submission"]
        assert submission["submitted_by"] == "delegate"
        assert submission["submitted_by_id"] == "del-001"
        assert submission["reason"] == "Study complete"
        assert "submitted_at" in submission

    def test_review_submission_records_truthful_actor_for_non_delegate(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Controller packet",
            summary="Summary",
            created_by_kind=OwnerKind.CONTROLLER,
            created_by_id="ctrl-001",
        )
        updates = transition_to_review(
            pkt,
            triggered_by_kind=OwnerKind.CONTROLLER,
            triggered_by_id="ctrl-001",
            trigger_reason="Controller submitted for review",
        )
        submission = updates["metadata"]["review_submission"]
        assert updates["metadata"]["review_submitted_by"] == "controller"
        assert updates["metadata"]["review_submitted_by_id"] == "ctrl-001"
        assert submission["submitted_by"] == "controller"
        assert submission["submitted_by_id"] == "ctrl-001"

    def test_review_submitted_does_not_mutate_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        original_status = pkt.status
        transition_to_review(pkt, OwnerKind.DELEGATE, "del-001")
        assert pkt.status == original_status  # immutable

    def test_cannot_review_non_draft(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        # First transition to review
        transition_to_review(pkt, OwnerKind.DELEGATE, "del-001")

        # Simulate a pending_review packet
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        with pytest.raises(PacketTransitionError, match="cannot transition to review"):
            transition_to_review(pending_pkt, OwnerKind.DELEGATE, "del-001")

    def test_cannot_review_accepted_packet(self):
        accepted_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id=None,
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Accepted",
            summary="Done",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="controller",
            created_by_id="ctrl-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
        )
        with pytest.raises(PacketTransitionError):
            transition_to_review(accepted_pkt, OwnerKind.CONTROLLER, "ctrl-001")

    def test_cannot_transition_to_review_without_actor_id(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        with pytest.raises(PacketTransitionError, match="non-empty triggered_by_id"):
            transition_to_review(pkt, OwnerKind.DELEGATE, "")


# ──────────────────────────────────────────────────────────────
# Accept Packet
# ──────────────────────────────────────────────────────────────

class TestAcceptPacket:
    def test_accept_pending_review_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        # First transition to review
        review_updates = transition_to_review(pkt, OwnerKind.DELEGATE, "del-001")
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })

        # Accept with upstream linkage
        accept_updates = accept_packet(
            pending_pkt,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
            acceptance_reason="Quality check passed",
        )
        assert accept_updates["status"] == PacketStatus.ACCEPTED
        assert accept_updates["accepted_at"] is not None
        linkage = accept_updates["metadata"]["acceptance"]
        assert linkage["accepted_by"] == "controller"
        assert linkage["accepted_by_id"] == "ctrl-001"
        assert linkage["upstream_task_id"] == "task-1"
        assert linkage["upstream_task_status"] == "done"
        assert linkage["acceptance_reason"] == "Quality check passed"

    def test_accept_records_accepted_at(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        updates = accept_packet(
            pending_pkt,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
        )
        assert updates["accepted_at"] is not None
        datetime.fromisoformat(updates["accepted_at"])  # valid ISO format

    def test_cannot_accept_draft_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        with pytest.raises(PacketTransitionError, match="expected 'pending_review'"):
            accept_packet(pkt, OwnerKind.CONTROLLER, "ctrl-001")

    def test_cannot_accept_already_accepted_packet(self):
        accepted_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id=None,
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Accepted",
            summary="Done",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="controller",
            created_by_id="ctrl-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
        )
        with pytest.raises(PacketTransitionError):
            accept_packet(accepted_pkt, OwnerKind.CONTROLLER, "ctrl-001")

    def test_accept_does_not_mutate_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        original_status = pending_pkt.status
        accept_packet(pending_pkt, OwnerKind.CONTROLLER, "ctrl-001",
                      upstream_task_id="task-1", upstream_task_status="done")
        assert pending_pkt.status == original_status  # immutable


# ──────────────────────────────────────────────────────────────
# Trust Boundary – The Critical Tests
# ──────────────────────────────────────────────────────────────

class TestTrustBoundary:
    """Trust boundary: packet existence != trust."""

    def test_draft_packet_not_trusted(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        assert pkt.is_trusted is False
        assert is_packet_trusted(pkt) is False

    def test_pending_review_packet_not_trusted(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        assert pending_pkt.is_trusted is False
        assert is_packet_trusted(pending_pkt) is False

    def test_delegate_cannot_self_accept(self):
        """Delegate cannot promote their own packet to accepted."""
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="My work",
            summary="I did the thing",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        # Delegate trying to self-accept should fail at status level
        with pytest.raises(PacketTransitionError):
            accept_packet(pending_pkt, OwnerKind.DELEGATE, "del-001")

    def test_accepted_packet_with_linkage_is_trusted(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        accept_updates = accept_packet(
            pending_pkt,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
        )
        accepted_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.ACCEPTED,
            "accepted_at": accept_updates["accepted_at"],
            "metadata": accept_updates["metadata"],
        })
        assert accepted_pkt.is_trusted is True
        assert is_packet_trusted(accepted_pkt) is True

    def test_non_accepted_packets_excluded_from_trusted_recall(self):
        """Only accepted packets pass the recall gate."""
        packets = [
            create_packet(
                project_id="proj-1",
                packet_type="study_result",
                title=f"Packet {i}",
                summary=f"Summary {i}",
                created_by_kind=OwnerKind.DELEGATE,
                created_by_id="del-001",
            )
            for i in range(5)
        ]
        # Mark one as accepted
        pending = MemoryPacket.from_dict({
            **packets[2].to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        accept_updates = accept_packet(
            pending,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
        )
        packets[2] = MemoryPacket.from_dict({
            **packets[2].to_dict(),
            "status": PacketStatus.ACCEPTED,
            "accepted_at": accept_updates["accepted_at"],
            "metadata": accept_updates["metadata"],
        })

        trusted = get_trusted_packets(packets)
        assert len(trusted) == 1
        assert trusted[0].memory_packet_id == packets[2].memory_packet_id

    def test_trusted_recall_with_mixed_statuses(self):
        """Mixed list: draft, pending_review, accepted – only accepted trusted."""
        draft = create_packet(
            project_id="proj-1",
            packet_type="draft_type",
            title="Draft",
            summary="Not trusted",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending = MemoryPacket.from_dict({
            **create_packet(
                project_id="proj-1",
                packet_type="pending_type",
                title="Pending",
                summary="Not trusted",
                created_by_kind=OwnerKind.DELEGATE,
                created_by_id="del-001",
            ).to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        accepted = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-1",
            packet_type="accepted_type",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Accepted",
            summary="Trusted",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-1",
                    "upstream_task_status": "done",
                }
            },
        )

        trusted = get_trusted_packets([draft, pending, accepted])
        assert len(trusted) == 1
        assert trusted[0].memory_packet_id == accepted.memory_packet_id

    def test_accepted_without_upstream_linkage_not_trusted(self):
        """FIX: Packet with acceptance but no upstream linkage is NOT trusted."""
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id=None,
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="No upstream",
            summary="Has accepted_by but no upstream linkage",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    # No upstream_task_id or upstream_decision_id
                }
            },
        )
        assert pkt.is_trusted is True  # accepted_at set
        assert is_packet_trusted(pkt) is False  # no upstream linkage

    def test_trust_boundary_validation(self):
        """validate_packet_trust_boundary returns detailed reason."""
        # Draft packet
        draft = create_packet(
            project_id="proj-1",
            packet_type="test",
            title="Draft",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        trusted, reason = validate_packet_trust_boundary(draft)
        assert trusted is False
        assert "not 'accepted'" in reason

        # Pending review packet
        pending = MemoryPacket.from_dict({
            **draft.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        trusted, reason = validate_packet_trust_boundary(pending)
        assert trusted is False
        assert "not 'accepted'" in reason

        # Accepted with upstream linkage
        accepted_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-1",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Accepted",
            summary="Trusted",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-1",
                    "upstream_task_status": "done",
                }
            },
        )
        trusted, reason = validate_packet_trust_boundary(accepted_pkt)
        assert trusted is True
        assert "trusted" in reason.lower()


# ──────────────────────────────────────────────────────────────
# Trust-Boundary Proof
# ──────────────────────────────────────────────────────────────

class TestTrustBoundaryProof:
    """Prove the complete trust boundary for memory packets."""

    def test_delegate_packet_lifecycle_cannot_self_promote(self):
        """Full lifecycle proof: delegate creates, submits, but cannot accept."""
        # Step 1: Delegate creates draft packet
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="My research",
            summary="Found important things",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
            task_id="task-1",
        )
        assert pkt.status == PacketStatus.DRAFT
        assert pkt.is_trusted is False

        # Step 2: Delegate submits for review
        review_updates = transition_to_review(pkt, OwnerKind.DELEGATE, "del-001")
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        assert pending_pkt.status == PacketStatus.PENDING_REVIEW
        assert pending_pkt.is_trusted is False

        # Step 3: Delegate tries to self-accept – MUST FAIL
        with pytest.raises(PacketTransitionError):
            accept_packet(pending_pkt, OwnerKind.DELEGATE, "del-001")

        # Step 4: Controller accepts with upstream linkage
        accept_updates = accept_packet(
            pending_pkt,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
        )
        accepted_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.ACCEPTED,
            "accepted_at": accept_updates["accepted_at"],
            "metadata": accept_updates["metadata"],
        })
        assert accepted_pkt.is_trusted is True
        assert is_packet_trusted(accepted_pkt) is True
        assert accepted_pkt.metadata["acceptance"]["upstream_task_id"] == "task-1"

    def test_non_accepted_excluded_from_trusted_recall(self):
        """Verify: non-accepted packets are excluded from trusted recall paths."""
        # Create various non-trusted packets
        packets = []
        for i in range(10):
            pkt = create_packet(
                project_id="proj-1",
                packet_type="study_result",
                title=f"Packet {i}",
                summary=f"Summary {i}",
                created_by_kind=OwnerKind.DELEGATE,
                created_by_id="del-001",
            )
            packets.append(pkt)

        # Make 2 accepted
        trusted_ids = set()
        for idx in [3, 7]:
            pending = MemoryPacket.from_dict({
                **packets[idx].to_dict(),
                "status": PacketStatus.PENDING_REVIEW,
            })
            accept_updates = accept_packet(
                pending,
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="ctrl-001",
                upstream_task_id=f"task-{idx}",
                upstream_task_status="done",
            )
            packets[idx] = MemoryPacket.from_dict({
                **packets[idx].to_dict(),
                "status": PacketStatus.ACCEPTED,
                "accepted_at": accept_updates["accepted_at"],
                "metadata": accept_updates["metadata"],
            })
            trusted_ids.add(packets[idx].memory_packet_id)

        # Recall only trusted
        trusted = get_trusted_packets(packets)
        assert len(trusted) == 2
        trusted_pkt_ids = {p.memory_packet_id for p in trusted}
        assert trusted_pkt_ids == trusted_ids
        # All 8 non-accepted are excluded
        assert len(packets) - len(trusted) == 8

    def test_explicit_upstream_linkage_required(self):
        """Trust requires explicit upstream linkage, not implicit acceptance."""
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })

        # Accept with explicit upstream linkage
        updates = accept_packet(
            pending,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            upstream_task_status="done",
        )
        linkage = updates["metadata"]["acceptance"]
        assert "upstream_task_id" in linkage
        assert "upstream_task_status" in linkage


# ──────────────────────────────────────────────────────────────
# Soft Delete
# ──────────────────────────────────────────────────────────────

class TestSoftDelete:
    def test_soft_delete_draft_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        updates = soft_delete_packet(pkt, reason="No longer needed")
        assert updates["metadata"]["deleted"] is True
        assert "deleted_at" in updates["metadata"]
        assert updates["metadata"]["deleted_reason"] == "No longer needed"

    def test_soft_delete_pending_review_packet(self):
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        updates = soft_delete_packet(pending)
        assert updates["metadata"]["deleted"] is True

    def test_cannot_soft_delete_accepted_packet(self):
        """Accepted packets are part of the trust chain and must not be removed."""
        accepted_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-1",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Accepted",
            summary="Trusted",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-1",
                    "upstream_task_status": "done",
                }
            },
        )
        with pytest.raises(PacketTransitionError, match="Cannot soft-delete accepted"):
            soft_delete_packet(accepted_pkt)


# ──────────────────────────────────────────────────────────────
# Packet Parent Linkage
# ──────────────────────────────────────────────────────────────

class TestPacketParentLinkage:
    def test_parent_packet_reference(self):
        parent = create_packet(
            project_id="proj-1",
            packet_type="checkpoint",
            title="v1",
            summary="Initial checkpoint",
            created_by_kind=OwnerKind.RUNTIME,
            created_by_id="runtime",
        )
        child = create_packet(
            project_id="proj-1",
            packet_type="checkpoint",
            title="v2",
            summary="Updated checkpoint",
            created_by_kind=OwnerKind.RUNTIME,
            created_by_id="runtime",
            parent_packet_id=parent.memory_packet_id,
        )
        assert child.parent_packet_id == parent.memory_packet_id


# ──────────────────────────────────────────────────────────────
# R1-A1 Hardening: Upstream Existence Verification
# ──────────────────────────────────────────────────────────────

class TestUpstreamExistenceVerification:
    """R1-A1: Trust requires upstream object existence, not just linkage presence.

    These tests prove that when a verifier is provided:
    - Packets with real upstream objects pass trust
    - Packets with fake/missing upstream objects fail trust
    - Acceptance is rejected if upstream object doesn't exist
    """

    def _make_verifier(self, existing_objects: dict[str, set[str]]):
        """Create a mock upstream existence verifier.

        Args:
            existing_objects: {object_type: {object_id, ...}}
                e.g., {"task": {"task-1", "task-2"}, "decision": {"dec-1"}}
        """
        def verify(object_type: str, object_id: str) -> bool:
            return object_id in existing_objects.get(object_type, set())
        return verify

    def test_trusted_packet_with_real_upstream_object(self):
        """Packet with real upstream task passes trust verification."""
        verifier = self._make_verifier({"task": {"task-1"}})
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-1",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Trusted",
            summary="Real upstream",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-1",
                    "upstream_task_status": "done",
                }
            },
        )
        assert is_packet_trusted(pkt, verify_upstream_exists=verifier) is True

    def test_trusted_packet_with_fake_upstream_task(self):
        """Packet with fake/missing upstream task fails trust verification."""
        verifier = self._make_verifier({"task": set()})  # no tasks exist
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-fake",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Fake upstream",
            summary="References non-existent task",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-nonexistent",
                    "upstream_task_status": "done",
                }
            },
        )
        # Without verifier: passes (linkage exists)
        assert is_packet_trusted(pkt) is True
        # With verifier: fails (upstream object doesn't exist)
        assert is_packet_trusted(pkt, verify_upstream_exists=verifier) is False

    def test_trusted_packet_with_fake_upstream_decision(self):
        """Packet with fake upstream decision fails trust verification."""
        verifier = self._make_verifier({"decision": set()})  # no decisions exist
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id=None,
            packet_type="decision_snapshot",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Fake decision",
            summary="References non-existent decision",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_decision_id": "dec-nonexistent",
                }
            },
        )
        assert is_packet_trusted(pkt, verify_upstream_exists=verifier) is False

    def test_acceptance_rejected_when_upstream_task_missing(self):
        """accept_packet raises error when upstream task doesn't exist."""
        verifier = self._make_verifier({"task": set()})
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        with pytest.raises(PacketTransitionError, match="does not exist in Postgres"):
            accept_packet(
                pending_pkt,
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="ctrl-001",
                upstream_task_id="task-nonexistent",
                verify_upstream_exists=verifier,
            )

    def test_acceptance_rejected_when_upstream_decision_missing(self):
        """accept_packet raises error when upstream decision doesn't exist."""
        verifier = self._make_verifier({"decision": set()})
        pkt = create_packet(
            project_id="proj-1",
            packet_type="decision_snapshot",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        with pytest.raises(PacketTransitionError, match="does not exist in Postgres"):
            accept_packet(
                pending_pkt,
                accepted_by_kind=OwnerKind.CONTROLLER,
                accepted_by_id="ctrl-001",
                upstream_decision_id="dec-nonexistent",
                verify_upstream_exists=verifier,
            )

    def test_acceptance_succeeds_when_upstream_exists(self):
        """accept_packet succeeds when upstream object exists."""
        verifier = self._make_verifier({"task": {"task-1"}})
        pkt = create_packet(
            project_id="proj-1",
            packet_type="study_result",
            title="Test",
            summary="Summary",
            created_by_kind=OwnerKind.DELEGATE,
            created_by_id="del-001",
        )
        pending_pkt = MemoryPacket.from_dict({
            **pkt.to_dict(),
            "status": PacketStatus.PENDING_REVIEW,
        })
        # Should NOT raise
        updates = accept_packet(
            pending_pkt,
            accepted_by_kind=OwnerKind.CONTROLLER,
            accepted_by_id="ctrl-001",
            upstream_task_id="task-1",
            verify_upstream_exists=verifier,
        )
        assert updates["status"] == PacketStatus.ACCEPTED
        assert updates["accepted_at"] is not None

    def test_trust_boundary_validation_with_fake_upstream(self):
        """validate_packet_trust_boundary reports fake upstream as untrusted."""
        verifier = self._make_verifier({"task": set()})
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-fake",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Fake",
            summary="Fake upstream",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-fake",
                }
            },
        )
        trusted, reason = validate_packet_trust_boundary(pkt, verify_upstream_exists=verifier)
        assert trusted is False
        assert "does not exist" in reason

    def test_get_trusted_packets_filters_fake_upstream(self):
        """get_trusted_packets excludes packets with fake upstream references."""
        verifier = self._make_verifier({"task": {"task-1"}})

        # Real upstream packet
        real_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-1",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Real",
            summary="Real upstream",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-1",
                }
            },
        )

        # Fake upstream packet
        fake_pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-ghost",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Fake",
            summary="Fake upstream",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-ghost",
                }
            },
        )

        # Without verifier: both pass (linkage exists)
        trusted_no_verify = get_trusted_packets([real_pkt, fake_pkt])
        assert len(trusted_no_verify) == 2

        # With verifier: only real upstream passes
        trusted_with_verify = get_trusted_packets(
            [real_pkt, fake_pkt], verify_upstream_exists=verifier
        )
        assert len(trusted_with_verify) == 1
        assert trusted_with_verify[0].memory_packet_id == real_pkt.memory_packet_id

    def test_verifier_not_required_for_backward_compat(self):
        """When no verifier is provided, legacy linkage-only check still works."""
        pkt = MemoryPacket(
            memory_packet_id=str(uuid4()),
            project_id="proj-1",
            task_id="task-nonexistent",
            packet_type="study_result",
            status=PacketStatus.ACCEPTED,
            acceptance_trigger=None,
            title="Legacy",
            summary="No verifier",
            storage_ref=None,
            content_hash=None,
            parent_packet_id=None,
            created_by_kind="delegate",
            created_by_id="del-001",
            created_at=datetime.now(timezone.utc).isoformat(),
            accepted_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "acceptance": {
                    "accepted_by": "controller",
                    "accepted_by_id": "ctrl-001",
                    "upstream_task_id": "task-nonexistent",
                }
            },
        )
        # Without verifier: passes (legacy behavior preserved)
        assert is_packet_trusted(pkt) is True
        assert is_packet_trusted(pkt, verify_upstream_exists=None) is True
