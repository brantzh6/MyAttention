"""
IKE v0 Typed ID Helpers

Provides lightweight typed ID generation, validation, and parsing
for IKE v0 object classes using prefixed identifiers.

ID Format: ike:{kind}:{uuid}
Example: ike:observation:550e8400-e29b-41d4-a716-446655440000
"""

import re
import uuid
from enum import Enum
from typing import Optional, Tuple


class IKEKind(str, Enum):
    """Valid IKE v0 object kind identifiers."""
    OBSERVATION = "observation"
    ENTITY = "entity"
    CLAIM = "claim"
    RESEARCH_TASK = "research_task"
    EXPERIMENT = "experiment"
    DECISION = "decision"
    HARNESS_CASE = "harness_case"


# Prefix mapping for all supported v0 object kinds
IKE_ID_PREFIXES = {
    IKEKind.OBSERVATION: "ike:observation:",
    IKEKind.ENTITY: "ike:entity:",
    IKEKind.CLAIM: "ike:claim:",
    IKEKind.RESEARCH_TASK: "ike:research_task:",
    IKEKind.EXPERIMENT: "ike:experiment:",
    IKEKind.DECISION: "ike:decision:",
    IKEKind.HARNESS_CASE: "ike:harness_case:",
}

# Regex pattern for validating IKE IDs
# Matches: ike:{kind}:{uuid} where kind is alphanumeric/underscore and uuid is standard format
IKE_ID_PATTERN = re.compile(
    r"^ike:([a-z_]+):([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)


def generate_ike_id(kind: IKEKind | str, uuid_value: Optional[str] = None) -> str:
    """
    Generate a typed IKE ID with prefix.

    Args:
        kind: The object kind (IKEKind enum or string like 'observation')
        uuid_value: Optional UUID string. If None, generates a new UUID4.

    Returns:
        Prefixed ID string in format: ike:{kind}:{uuid}

    Example:
        >>> generate_ike_id(IKEKind.OBSERVATION)
        'ike:observation:550e8400-e29b-41d4-a716-446655440000'
    """
    if isinstance(kind, str):
        kind = IKEKind(kind)

    if uuid_value is None:
        uuid_value = str(uuid.uuid4())

    prefix = IKE_ID_PREFIXES.get(kind)
    if prefix is None:
        raise ValueError(f"Unknown IKE kind: {kind}")

    return f"{prefix}{uuid_value}"


def validate_ike_id(ike_id: str) -> bool:
    """
    Validate that an ID string matches the expected IKE format.

    Args:
        ike_id: The ID string to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_ike_id("ike:observation:550e8400-e29b-41d4-a716-446655440000")
        True
        >>> validate_ike_id("invalid-id")
        False
    """
    match = IKE_ID_PATTERN.match(ike_id)
    if not match:
        return False

    kind_str = match.group(1)
    try:
        IKEKind(kind_str)
        return True
    except ValueError:
        return False


def parse_ike_id(ike_id: str) -> Tuple[IKEKind, str]:
    """
    Parse an IKE ID into its kind and UUID components.

    Args:
        ike_id: The prefixed ID string to parse

    Returns:
        Tuple of (IKEKind, uuid_string)

    Raises:
        ValueError: If the ID format is invalid

    Example:
        >>> parse_ike_id("ike:observation:550e8400-e29b-41d4-a716-446655440000")
        (<IKEKind.OBSERVATION: 'observation'>, '550e8400-e29b-41d4-a716-446655440000')
    """
    match = IKE_ID_PATTERN.match(ike_id)
    if not match:
        raise ValueError(f"Invalid IKE ID format: {ike_id}")

    kind_str = match.group(1)
    uuid_str = match.group(2)

    try:
        kind = IKEKind(kind_str)
    except ValueError:
        raise ValueError(f"Unknown IKE kind in ID: {kind_str}")

    return (kind, uuid_str)
