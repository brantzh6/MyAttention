# IKE Source Intelligence GitHub Signal Relation Hints Result

Date: 2026-05-02

Task ID: IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_2026-05-02

## Summary

Implemented deterministic relation hints for GitHub repo-scoped signal objects.

GitHub issue, discussion, and pull signal object keys now emit relation hints back to:

- the parent repository
- the repository owner as a person candidate

Related candidate seeding now also supports repository candidates, allowing a GitHub signal to seed its repository context without subscribing, promoting, or writing source plans.

## Files Changed

- `services/api/feeds/source_contracts.py`
- `services/api/feeds/source_postprocess.py`
- `services/api/feeds/source_semantics.py`
- `services/api/routers/feeds.py`
- `services/api/tests/test_source_discovery_identity.py`
- `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md`

## Why This Solution

The previous accepted slice made GitHub issues and discussions recognizable as stable `signal` objects across focus modes. This patch keeps that identity behavior unchanged and adds only URL-derived context links.

The implementation stays inside existing source-discovery mechanics:

- `_candidate_relation_hints(...)` emits advisory related objects.
- `_build_related_candidate_seed(...)` creates in-memory candidate seeds only.
- no GitHub API calls are introduced.
- no persistence, scheduler, source-plan promotion, or route contract behavior is changed.

This preserves the project direction that source value is contextual: a GitHub issue or discussion is more useful when attached to its repository and owner context.

## Validation Run

Passed:

```powershell
python -m pytest services/api/tests/test_source_discovery_identity.py -q
```

Observed result:

```text
45 passed, 6 warnings, 19 subtests passed
```

Passed:

```powershell
python -m py_compile services/api/routers/feeds.py services/api/tests/test_source_discovery_identity.py
```

Passed:

```powershell
python -m py_compile services/api/feeds/source_contracts.py services/api/feeds/source_postprocess.py services/api/feeds/source_semantics.py services/api/routers/feeds.py services/api/tests/test_source_discovery_identity.py
```

## Known Risks

- Repository related-candidate seeding is now allowed for relation hints. It remains advisory and in-memory, but downstream ranking should still be reviewed through the GitHub/Codex L1 gate before promotion.
- Existing repository-owner handling treats GitHub owners as `person` seeds. That matches the pre-existing behavior, but future work may need organization/person disambiguation.
- The broader worktree remains dirty and over budget; this result is not safe for broad commit or mixed PR.
- `services/api/feeds/source_contracts.py`, `services/api/feeds/source_postprocess.py`, and `services/api/feeds/source_semantics.py` are currently untracked but required by the scoped source-intelligence candidate. A PR that includes `feeds.py` without these files will be incomplete.

## Recommendation

accept_with_changes

Required changes before promotion:

- Run scoped GitHub/Codex L1 review on only this source-intelligence slice.
- Absorb any L1 findings locally.
- Controller performs L2 integration review before accepting promotion.
