# IKE Source Intelligence GitHub Signal Relation Hints Review Absorption

Date: 2026-05-02

Task ID: IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_2026-05-02

## Summary

The fixed GitHub signal relation-hints slice was re-reviewed and accepted.

The original correctness issue was a false-person-seed path for GitHub repo owners. The controller fixed that by:

- normalizing ambiguous single-segment GitHub/GitLab handles to `organization`
- changing GitHub repo-owner relation hints to `organization`
- keeping repository relation hints intact

## Files Changed

- `services/api/feeds/source_semantics.py`
- `services/api/routers/feeds.py`
- `services/api/tests/test_source_discovery_identity.py`
- `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md`
- `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_REVIEW_ABSORPTION_2026-05-02.md`

## Why This Solution

The accepted fix removes the concrete correctness issue without widening scope:

- signal identity behavior remains deterministic and URL-derived
- repository relation hints remain advisory and in-memory
- no GitHub APIs, scheduler behavior, persistence, or promotion semantics changed

The controller accepted the re-reviewed slice after validation passed.

## GitHub/Codex Review Absorption

Codex Cloud review on PR #2 returned three bounded findings:

1. `P1` unresolved `ai_judgment` import in `services/api/routers/feeds.py`
2. `P2` dropped `workshop` / `webinar` / `talks` event-page matching
3. `P2` missing reserved GitHub namespace guard for signal relation hints
4. `P0` updated-head still missing committed `ai_judgment` helper definitions

Absorption decision:

- `P1`: accepted as a PR packaging issue after the updated-head review showed the helper definitions were present locally but not committed to the PR branch.
- `P2 event matching`: accepted and fixed. Event segment matching now restores `workshop`, `webinar`, `talk`, and `talks`; regression coverage was added.
- `P2 reserved GitHub namespace`: accepted and fixed. Reserved repository-owner namespaces now block repo-shaped signal identity and relation hints while preserving `/orgs/<org>` as an organization object.
- `P0 missing helper definitions`: accepted and fixed. The shared `ai_judgment` helper substrate is now committed, and the route test expectation now allows relation-hint candidate expansion while still asserting the original GitHub issue remains a `signal`.

## Validation Run

Passed:

```powershell
python -m pytest services/api/tests/test_source_discovery_identity.py -q
```

Observed result:

```text
47 passed, 6 warnings, 23 subtests passed
```

Passed:

```powershell
python -m pytest services/api/tests/test_feeds_source_discovery_route.py -q
```

Observed result:

```text
37 passed, 4 warnings
```

Passed:

```powershell
python -m py_compile services/api/feeds/source_semantics.py services/api/routers/feeds.py services/api/feeds/ai_judgment.py services/api/tests/test_source_discovery_identity.py
```

## Known Risks

- Ambiguous single-segment GitHub/GitLab handles are now classified as `organization` to avoid false person seeds. That is conservative, but it may under-model user-profile pages until a better identity source exists.
- The broader worktree remains dirty and over budget; this result is not safe for broad commit or mixed PR.

## Recommendation

accept
