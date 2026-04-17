"""
IKE v0 Procedural Memory Runtime

Minimal file-based persistence for procedural memory records.

This is the v1 prototype implementation - narrow scope, file-based storage,
triggered only at task_closure.

See: docs/IKE_CLAUDE_CODE_B3_PROTOTYPE_DECISION.md
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from ike_v0.schemas.procedural_memory import ProceduralMemory
from ike_v0.types.ids import generate_ike_id, IKEKind


# Default storage directory for procedural memories
# Resolves to repository root: <repo-root>\.runtime\procedural_memories
DEFAULT_PROCEDURAL_MEMORY_DIR = Path(__file__).parent.parent.parent.parent.parent / ".runtime" / "procedural_memories"


class ProceduralMemoryStore:
    """
    File-based store for procedural memory records.

    This is a minimal prototype implementation:
    - Flat directory structure
    - One JSON file per memory record
    - Human-inspectable format
    - No automatic recall/injection (v1 scope)

    Attributes:
        storage_dir: Directory where memory records are persisted
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the procedural memory store.

        Args:
            storage_dir: Optional custom storage directory. Defaults to
                        .runtime/procedural_memories in project root.
        """
        self.storage_dir = storage_dir or DEFAULT_PROCEDURAL_MEMORY_DIR
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _generate_memory_id(self, title: str, created_at: datetime) -> str:
        """
        Generate a unique memory ID using IKE typed ID format.

        Args:
            title: Memory title (not used in ID, kept for signature compatibility)
            created_at: Creation timestamp (not used in ID, kept for signature compatibility)

        Returns:
            Unique memory ID in format 'ike:procedure:{uuid}'
        """
        return generate_ike_id(IKEKind.PROCEDURE)

    def create_procedure(
        self,
        title: str,
        lesson: str,
        why_it_mattered: str,
        how_to_apply: str,
        confidence: float,
        source_artifact_ref: str,
        memory_id: Optional[str] = None,
    ) -> ProceduralMemory:
        """
        Create a new procedural memory record.

        This is the primary entry point for capturing a procedure from task closure.

        Args:
            title: Short title for the procedural lesson
            lesson: The core procedural lesson learned
            why_it_mattered: Why this lesson mattered in context
            how_to_apply: Concrete guidance on how to apply this lesson
            confidence: Confidence in this lesson (0.0 to 1.0)
            source_artifact_ref: Reference to the source artifact (e.g., task closure ID)
            memory_id: Optional custom memory ID. If not provided, auto-generated.

        Returns:
            ProceduralMemory object (not yet persisted)

        Usage notes:
            - This creates the record in memory only
            - Call persist() to write to disk
            - All fields are required per B3 prototype decision
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")

        created_at = datetime.now(timezone.utc)

        if memory_id is None:
            memory_id = self._generate_memory_id(title, created_at)

        return ProceduralMemory(
            id=memory_id,
            kind="procedure",
            memory_type="procedure",
            title=title,
            lesson=lesson,
            why_it_mattered=why_it_mattered,
            how_to_apply=how_to_apply,
            confidence=confidence,
            source_artifact_ref=source_artifact_ref,
            created_from="task_closure",
            created_at=created_at,
        )

    def _id_to_filename(self, memory_id: str) -> str:
        """
        Convert a memory ID to a safe filename.

        Replaces colons with underscores for filesystem compatibility.

        Args:
            memory_id: Memory ID (e.g., 'ike:procedure:{uuid}')

        Returns:
            Safe filename without colons
        """
        return memory_id.replace(":", "_") + ".json"

    def _filename_to_id(self, filename: str) -> str:
        """
        Convert a filename back to a memory ID.

        Replaces underscores with colons to reconstruct the ID.

        Args:
            filename: Filename (e.g., 'ike_procedure_{uuid}.json')

        Returns:
            Memory ID with colons
        """
        # Remove .json extension and convert back
        base = filename[:-5] if filename.endswith(".json") else filename
        return base.replace("_", ":", 2)  # Only replace first two underscores (ike_procedure_ -> ike:procedure:)

    def persist(self, memory: ProceduralMemory) -> Path:
        """
        Persist a procedural memory to disk.

        Args:
            memory: ProceduralMemory object to persist

        Returns:
            Path to the persisted JSON file

        File format:
            - One JSON file per memory
            - Filename: {memory.id}.json (with colons replaced by underscores)
            - Human-inspectable pretty-printed JSON
        """
        filename = self._id_to_filename(memory.id)
        filepath = self.storage_dir / filename

        # Serialize to JSON (pretty-printed for human inspection)
        data = memory.model_dump(mode="json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def capture_from_task_closure(
        self,
        title: str,
        lesson: str,
        why_it_mattered: str,
        how_to_apply: str,
        confidence: float,
        source_artifact_ref: str,
        memory_id: Optional[str] = None,
    ) -> Path:
        """
        Capture and persist a procedural memory from task closure.

        This is the convenience method that combines create + persist.
        This is the primary pathway for the v1 prototype.

        Args:
            title: Short title for the procedural lesson
            lesson: The core procedural lesson learned
            why_it_mattered: Why this lesson mattered in context
            how_to_apply: Concrete guidance on how to apply this lesson
            confidence: Confidence in this lesson (0.0 to 1.0)
            source_artifact_ref: Reference to the source artifact (e.g., task closure ID)
            memory_id: Optional custom memory ID

        Returns:
            Path to the persisted JSON file

        Usage notes:
            - This is the main entry point for task_closure trigger
            - Creates and persists in one call
            - File is immediately human-inspectable
        """
        memory = self.create_procedure(
            title=title,
            lesson=lesson,
            why_it_mattered=why_it_mattered,
            how_to_apply=how_to_apply,
            confidence=confidence,
            source_artifact_ref=source_artifact_ref,
            memory_id=memory_id,
        )
        return self.persist(memory)

    def load(self, memory_id: str) -> Optional[ProceduralMemory]:
        """
        Load a procedural memory from disk.

        Args:
            memory_id: ID of the memory to load (e.g., 'ike:procedure:{uuid}')

        Returns:
            ProceduralMemory object if found, None otherwise
        """
        filename = self._id_to_filename(memory_id)
        filepath = self.storage_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ProceduralMemory(**data)

    def list_all(self) -> List[ProceduralMemory]:
        """
        List all persisted procedural memories.

        Returns:
            List of all ProceduralMemory objects in storage

        Usage notes:
            - Loads all memories into memory
            - Returns empty list if storage is empty
            - No sorting guaranteed (use sorted() if needed)
        """
        memories = []

        for filepath in self.storage_dir.glob("ike_procedure_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                memory = ProceduralMemory(**data)
                memories.append(memory)
            except (json.JSONDecodeError, Exception):
                # Skip corrupted files
                continue

        return memories

    def count(self) -> int:
        """
        Count the number of persisted procedural memories.

        Returns:
            Number of JSON files in storage directory
        """
        return len(list(self.storage_dir.glob("*.json")))

    def delete(self, memory_id: str) -> bool:
        """
        Delete a procedural memory from disk.

        Args:
            memory_id: ID of the memory to delete (e.g., 'ike:procedure:{uuid}')

        Returns:
            True if deleted, False if not found

        Usage notes:
            - This is for manual cleanup/testing
            - No undo - file is permanently deleted
        """
        filename = self._id_to_filename(memory_id)
        filepath = self.storage_dir / filename

        if not filepath.exists():
            return False

        filepath.unlink()
        return True


# Convenience functions for simple usage

_default_store: Optional[ProceduralMemoryStore] = None


def get_default_store() -> ProceduralMemoryStore:
    """Get or create the default procedural memory store."""
    global _default_store
    if _default_store is None:
        _default_store = ProceduralMemoryStore()
    return _default_store


def capture_procedure(
    title: str,
    lesson: str,
    why_it_mattered: str,
    how_to_apply: str,
    confidence: float,
    source_artifact_ref: str,
) -> Path:
    """
    Capture a procedural memory using the default store.

    This is the simplest entry point for task_closure capture.

    Args:
        title: Short title for the procedural lesson
        lesson: The core procedural lesson learned
        why_it_mattered: Why this lesson mattered in context
        how_to_apply: Concrete guidance on how to apply this lesson
        confidence: Confidence in this lesson (0.0 to 1.0)
        source_artifact_ref: Reference to the source artifact

    Returns:
        Path to the persisted JSON file
    """
    store = get_default_store()
    return store.capture_from_task_closure(
        title=title,
        lesson=lesson,
        why_it_mattered=why_it_mattered,
        how_to_apply=how_to_apply,
        confidence=confidence,
        source_artifact_ref=source_artifact_ref,
    )


# Closure Adapter - validates and passes through explicit closure payload

class TaskClosurePayload:
    """
    Explicit task closure payload for procedural memory capture.

    This is a narrow data class that holds the procedural memory fields
    as explicitly decided elsewhere (not derived by this adapter).

    Attributes:
        title: Short title for the procedural lesson
        lesson: The core procedural lesson learned (explicit, not derived)
        why_it_mattered: Why this lesson mattered in context (explicit)
        how_to_apply: Concrete guidance on how to apply (explicit)
        confidence: Confidence in this lesson 0.0-1.0 (explicit)
        source_artifact_ref: Reference to the source artifact (e.g., chain_id)
    """

    def __init__(
        self,
        title: str,
        lesson: str,
        why_it_mattered: str,
        how_to_apply: str,
        confidence: float,
        source_artifact_ref: str,
    ):
        self.title = title
        self.lesson = lesson
        self.why_it_mattered = why_it_mattered
        self.how_to_apply = how_to_apply
        self.confidence = confidence
        self.source_artifact_ref = source_artifact_ref


def validate_closure_payload(payload: Dict[str, Any]) -> TaskClosurePayload:
    """
    Validate and normalize an explicit closure payload.

    This is a narrow adapter that only validates required fields and
    normalizes the shape for procedural-memory persistence.

    Args:
        payload: Dict with keys: title, lesson, why_it_mattered, how_to_apply,
                 confidence, source_artifact_ref

    Returns:
        TaskClosurePayload object with validated fields

    Raises:
        ValueError: If any required field is missing or invalid

    Usage notes:
        - This adapter does NOT derive or fabricate content
        - All fields must be explicitly provided
        - Pass the result to capture_procedure_from_payload()
    """
    required_fields = ["title", "lesson", "why_it_mattered", "how_to_apply", "confidence", "source_artifact_ref"]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # Validate confidence range
    confidence = payload["confidence"]
    if not isinstance(confidence, (int, float)):
        raise ValueError(f"Confidence must be a number, got {type(confidence)}")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")

    # Validate string fields are non-empty
    for field in ["title", "lesson", "why_it_mattered", "how_to_apply", "source_artifact_ref"]:
        value = payload[field]
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string, got {type(value)}")
        if not value.strip():
            raise ValueError(f"{field} cannot be empty")

    return TaskClosurePayload(
        title=payload["title"],
        lesson=payload["lesson"],
        why_it_mattered=payload["why_it_mattered"],
        how_to_apply=payload["how_to_apply"],
        confidence=float(payload["confidence"]),
        source_artifact_ref=payload["source_artifact_ref"],
    )


def capture_procedure_from_payload(payload: Dict[str, Any], memory_id: Optional[str] = None) -> Path:
    """
    Capture and persist a procedural memory from an explicit closure payload.

    This is the primary entry point for task_closure capture in v1.
    The adapter only validates and passes through - no content derivation.

    Args:
        payload: Dict with keys: title, lesson, why_it_mattered, how_to_apply,
                 confidence, source_artifact_ref
        memory_id: Optional custom memory ID (auto-generated if not provided)

    Returns:
        Path to the persisted JSON file

    Raises:
        ValueError: If payload validation fails

    Usage notes:
        - This adapter does NOT derive or fabricate content
        - All procedural memory fields must be explicitly provided
        - Validation fails clearly if input is insufficient
        - Persists to file-based storage immediately

    See also:
        - validate_closure_payload() for validation only
        - capture_procedure() for direct field input
    """
    # Validate and normalize payload
    validated = validate_closure_payload(payload)

    # Capture using the existing store
    store = get_default_store()
    return store.capture_from_task_closure(
        title=validated.title,
        lesson=validated.lesson,
        why_it_mattered=validated.why_it_mattered,
        how_to_apply=validated.how_to_apply,
        confidence=validated.confidence,
        source_artifact_ref=validated.source_artifact_ref,
        memory_id=memory_id,
    )


# Benchmark Closure Memory Payload Helper

def create_benchmark_closure_payload(
    title: str,
    lesson: str,
    why_it_mattered: str,
    how_to_apply: str,
    confidence: float,
    source_artifact_ref: str,
) -> Dict[str, Any]:
    """
    Create an explicit procedural memory payload from a reviewed benchmark closure.

    This is a narrow helper for benchmark study closures to produce explicit
    payload fields that the procedural-memory adapter can consume truthfully.

    Args:
        title: Short title for the procedural lesson (explicit, not derived)
        lesson: The core procedural lesson learned (explicit, not derived)
        why_it_mattered: Why this lesson mattered in context (explicit)
        how_to_apply: Concrete guidance on how to apply (explicit)
        confidence: Confidence in this lesson 0.0-1.0 (explicit)
        source_artifact_ref: Reference to the source artifact (e.g., study result ID)

    Returns:
        Dict suitable for capture_procedure_from_payload()

    Usage notes:
        - This helper does NOT derive or fabricate content
        - All fields must be explicitly provided by the caller
        - Intended for reviewed benchmark study closures
        - Pass the result to capture_procedure_from_payload() for persistence

    Example:
        payload = create_benchmark_closure_payload(
            title="Three-tier audit structure for evaluation",
            lesson="Pre/in/post-action tiers provide concrete evaluation workflow",
            why_it_mattered="Enables structured visibility into agent operations",
            how_to_apply="Apply three-tier structure to evolution-layer evaluations",
            confidence=0.75,
            source_artifact_ref="SR-HARNESS-B4S4-8098e069",
        )
        filepath = capture_procedure_from_payload(payload)
    """
    return {
        "title": title,
        "lesson": lesson,
        "why_it_mattered": why_it_mattered,
        "how_to_apply": how_to_apply,
        "confidence": confidence,
        "source_artifact_ref": source_artifact_ref,
    }
