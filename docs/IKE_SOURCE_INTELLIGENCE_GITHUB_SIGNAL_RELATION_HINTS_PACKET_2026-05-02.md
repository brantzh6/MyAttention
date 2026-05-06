# IKE Source Intelligence GitHub Signal Relation Hints Packet

Date: 2026-05-02

Task ID: IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_2026-05-02

Risk: R2 if bounded to source-discovery identity and relation hints.

Lifecycle stage: Design packet; implementation not started.

## Purpose

Continue the source-intelligence quality mainline after GitHub issue/discussion identity recognition.

The last accepted slice recognized GitHub issues and discussions as `signal` objects across focus modes. The next narrow improvement is to make those signal objects carry relation hints back to their repository and owner context, so downstream ranking and review surfaces can see the signal in context instead of as an isolated URL.

## Problem

GitHub issue/discussion/pull URLs can now become stable signal objects, but source intelligence still loses too much context:

- a repo-scoped issue is related to a repository
- a repo-scoped discussion is related to a repository
- a pull request is related to a repository and usually useful as development activity evidence
- the repository owner can still seed a person/organization candidate through existing related-candidate mechanics

Without explicit relation hints, the system can recognize the signal but still under-use it for object-level source planning and person discovery.

## Desired Behavior

For GitHub repo-scoped signal object keys:

```text
github.com/{owner}/{repo}/issue/{id}
github.com/{owner}/{repo}/discussion/{id}
github.com/{owner}/{repo}/pull/{id}
```

`_candidate_relation_hints(...)` should emit at least:

- a `repository` relation pointing to `github.com/{owner}/{repo}`
- an owner relation compatible with the existing repository-owner person seed behavior, unless an existing reserved namespace rule blocks it

The behavior should remain deterministic and URL-derived. Do not call GitHub APIs.

## In Scope

Allowed files:

- `services/api/routers/feeds.py`
- `services/api/tests/test_source_discovery_identity.py`
- optional only if needed: `services/api/feeds/source_semantics.py`

Allowed implementation shape:

- extend `_candidate_relation_hints(...)`
- add focused unit tests for issue, discussion, and pull relation hints
- keep object identity behavior unchanged unless a test exposes a direct bug

## Out Of Scope

Do not change:

- frontend UI
- `/control`
- persistence schema
- scheduler logic
- source plan promotion semantics
- GitHub API integration
- AI judgment prompt semantics
- route response contracts beyond existing candidate fields

## Acceptance Criteria

1. Existing GitHub issue/discussion signal identity tests still pass.
2. New tests prove GitHub issue/discussion/pull signal objects produce repository relation hints.
3. New tests prove relation hints can seed a related repository candidate without faking subscription or promotion.
4. Existing reserved namespace protections are not weakened.
5. No non-source-intelligence files are changed.

## Validation

Required:

```powershell
cd D:\code\MyAttention
python -m pytest services/api/tests/test_source_discovery_identity.py -q
python -m py_compile services/api/routers/feeds.py services/api/tests/test_source_discovery_identity.py
```

Optional if `source_semantics.py` is edited:

```powershell
python -m py_compile services/api/feeds/source_semantics.py
```

Before PR:

```powershell
python scripts/governance/classify_worktree.py --cwd D:\code\MyAttention
git status --short
```

## Layered Review Gate

### L0 Scope Review

Controller must confirm:

- the task remains source-intelligence only
- allowed files are respected
- no runtime truth, persistence, or scheduler boundary is touched

### L1 Code Review

GitHub/Codex or delegated reviewer must check:

- relation parsing correctness
- no reserved namespace regression
- no fake backend data
- no unrelated cleanup

### L2 Integration Review

Controller must check:

- related candidate seed behavior remains advisory
- source plan promotion semantics are unchanged
- validation evidence is present

L3 is not required unless the implementation touches persistence, scheduler, worker harness, runtime truth, permissions, or promotion authority.

## Dirty Worktree Rule

This packet must not be implemented as a mixed worktree commit.

Promotion path:

1. isolate only the allowed source-intelligence files
2. stage only this packet result and implementation files
3. push a scoped branch
4. use GitHub/Codex review as L1 evidence
5. local Codex may fix review findings
6. controller decides acceptance

## Required Result Format

The implementation delegate must create:

```text
docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md
```

It must include:

- summary
- files_changed
- why_this_solution
- validation_run
- known_risks
- recommendation: `accept`, `accept_with_changes`, or `reject`

## Recommendation

accept as the next bounded mainline packet.
