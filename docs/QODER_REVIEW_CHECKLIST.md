# Qoder Review Checklist

Bring these back when asking for a review of qoder's work:

## Required

1. Task name
2. Exact scope
3. Files changed
4. Diff or commit hash
5. Validation commands and outputs
6. Known risks / unresolved items

## Strongly Recommended

1. Before/after screenshots for UI changes
2. Short explanation of why this patch is the smallest safe change
3. Explicit note if any backend behavior changed

## Review Outcomes

Possible outcomes:

- `accept`
- `accept_with_changes`
- `reject`

If any required item is missing, the default should be:

- `accept_with_changes` or `reject`

because the work is not auditable enough.
