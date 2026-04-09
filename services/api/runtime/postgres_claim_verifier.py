"""
IKE Runtime v0 - Postgres-backed ClaimVerifier

Narrow service-layer implementation of the runtime-owned claim truth boundary.
This module uses the current durable runtime truth sources:

- EXPLICIT_ASSIGNMENT -> runtime_tasks.owner_kind / owner_id
- ACTIVE_LEASE -> runtime_tasks.current_lease_id + runtime_worker_leases
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from db.models import RuntimeTask, RuntimeWorkerLease, RuntimeLeaseStatus
from runtime.leases import ClaimVerifier, ClaimVerificationResult
from runtime.state_machine import ClaimType, OwnerKind


class PostgresClaimVerifier(ClaimVerifier):
    """Verify delegate claims against the current runtime Postgres truth."""

    def __init__(self, db_session) -> None:
        self._db_session = db_session

    @staticmethod
    def _parse_uuid(value: str, field_name: str) -> UUID | None:
        try:
            return UUID(str(value))
        except (TypeError, ValueError):
            return None

    def verify_claim(
        self,
        claim_type: ClaimType,
        claim_ref: str,
        delegate_id: str,
        task_id: str,
    ) -> ClaimVerificationResult:
        task_uuid = self._parse_uuid(task_id, "task_id")
        if task_uuid is None:
            return ClaimVerificationResult(
                valid=False,
                error=f"Invalid task_id: {task_id}",
            )

        if claim_type == ClaimType.EXPLICIT_ASSIGNMENT:
            # For v0, task ownership fields are the durable truth for explicit
            # assignment. claim_ref must equal the task_id it proves.
            if str(claim_ref) != str(task_id):
                return ClaimVerificationResult(
                    valid=False,
                    error=(
                        "Explicit assignment claim_ref must match task_id under "
                        "the v0 ownership-truth model"
                    ),
                )

            result = self._db_session.execute(
                select(RuntimeTask.owner_kind, RuntimeTask.owner_id).where(
                    RuntimeTask.task_id == task_uuid
                )
            )
            row = result.one_or_none()
            if row is None:
                return ClaimVerificationResult(
                    valid=False,
                    error=f"Task not found for explicit assignment: {task_id}",
                )

            owner_kind, owner_id = row
            if owner_kind == OwnerKind.DELEGATE and owner_id == delegate_id:
                return ClaimVerificationResult(valid=True)
            return ClaimVerificationResult(
                valid=False,
                error=(
                    f"No explicit assignment found for delegate={delegate_id} "
                    f"on task={task_id}"
                ),
            )

        if claim_type == ClaimType.ACTIVE_LEASE:
            lease_uuid = self._parse_uuid(claim_ref, "claim_ref")
            if lease_uuid is None:
                return ClaimVerificationResult(
                    valid=False,
                    error=f"Invalid lease claim_ref: {claim_ref}",
                )

            result = self._db_session.execute(
                select(
                    RuntimeTask.current_lease_id,
                    RuntimeWorkerLease.owner_kind,
                    RuntimeWorkerLease.owner_id,
                    RuntimeWorkerLease.task_id,
                    RuntimeWorkerLease.lease_status,
                )
                .join(
                    RuntimeWorkerLease,
                    RuntimeWorkerLease.lease_id == RuntimeTask.current_lease_id,
                )
                .where(
                    RuntimeTask.task_id == task_uuid,
                    RuntimeWorkerLease.lease_id == lease_uuid,
                )
            )
            row = result.one_or_none()
            if row is None:
                return ClaimVerificationResult(
                    valid=False,
                    error=(
                        f"No active lease linkage found for lease_id={claim_ref}, "
                        f"task={task_id}"
                    ),
                )

            current_lease_id, owner_kind, owner_id, lease_task_id, lease_status = row
            if (
                str(current_lease_id) == str(lease_uuid)
                and owner_kind == OwnerKind.DELEGATE
                and owner_id == delegate_id
                and str(lease_task_id) == str(task_uuid)
                and lease_status == RuntimeLeaseStatus.ACTIVE
            ):
                return ClaimVerificationResult(valid=True)

            return ClaimVerificationResult(
                valid=False,
                error=(
                    f"Lease claim mismatch for delegate={delegate_id}, "
                    f"task={task_id}, lease_id={claim_ref}"
                ),
            )

        return ClaimVerificationResult(
            valid=False,
            error=f"Unknown claim type: {claim_type}",
        )
