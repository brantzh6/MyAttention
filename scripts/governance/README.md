# Governance Tooling

## Dirty Worktree Classifier

`classify_worktree.py` is a read-only helper for grouping `git status --short`
entries before scoped review preparation.

Human-readable report:

```powershell
python D:\code\MyAttention\scripts\governance\classify_worktree.py --cwd D:\code\MyAttention
```

Parseable JSON:

```powershell
python D:\code\MyAttention\scripts\governance\classify_worktree.py --cwd D:\code\MyAttention --json
```

Recommendations:

- `clean`: zero dirty or untracked entries
- `within_budget`: no more than 20 entries and no more than 3 populated groups
- `requires_scoped_review_prep`: over either budget threshold

The tool does not stage files, create branches, delete files, call GitHub, or
infer promotion status.
