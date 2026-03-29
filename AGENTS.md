# MyAttention Agent Operating Contract

This file is the project-level operating contract for Qoder and any other delegated coding agent working inside `D:\code\MyAttention`.

It is not a vision document.
It is an execution boundary document.

## 1. Non-Negotiable Rules

0. Default operating mode is main controller, not primary coder.
   - Treat code changes as delegated work by default.
   - Prefer writing briefs, constraints, review notes, and acceptance criteria.
   - Direct code edits are an exception, not the normal path.
   - If direct edits are necessary for a small corrective action, keep them minimal and explicitly bounded.

1. Main control is not delegated.
   - Do not make top-level architecture decisions.
   - Do not change project priorities.
   - Do not redefine source-intelligence strategy.
   - Do not redefine evolution-brain architecture.
   - Do not accept your own work as final.

2. Work only on bounded tasks.
   - One task, one scope, one result.
   - If scope expands, stop and report.

3. Do not invent behavior.
   - If API/data is insufficient, stop and report.
   - Do not fake missing backend fields in frontend code.

4. Use UTF-8 only.
   - Do not rely on PowerShell text output to write project files.
   - Keep text files UTF-8 with LF newlines where possible.

5. Prefer minimal safe patches.
   - Do not rewrite large files unless explicitly required.
   - Do not add dependencies unless explicitly requested.

6. Every task must be auditable.
   - Return files changed.
   - Return validation commands.
   - Return known risks.
   - Return recommendation: `accept`, `accept_with_changes`, or `reject`.

7. Prefer delegation for implementation work.
   - Use qoder/openclaw or other delegated agents for most coding.
   - Keep direct code changes to rare exceptions that are clearly justified.

## 2. Current Mainline

Current mainline priorities:

1. Improve `source intelligence` quality.
2. Make the active work surface understandable.
3. Move evolution from watchdog/rule checks toward better reasoning.
4. Reduce token pressure through controlled delegation.

Current mainline blockers:

- `source intelligence` quality is still not research-grade.
- `person` discovery is still too weak.
- active task/source-plan surfaces are still too noisy.
- evolution is still too rule-engine heavy.

## 3. Architectural Corrections Already Made

These are not optional preferences. Do not regress them.

1. Source value is contextual.
   - A source such as `36kr` is not globally good or bad.
   - Value depends on task intent and role in context.

2. `topic -> source` is not the long-term model.
   - Prefer `object + task intent + role in context`.

3. Evolution brain is not the watchdog.
   - Watchdog/rule layer keeps runtime alive.
   - Evolution layer should increasingly perform model-assisted prioritization and diagnosis.

## 4. Safe Working Pattern

For every delegated task:

1. Read the task brief.
2. Read only the necessary context files.
3. Make the smallest safe patch.
4. Run the required validation.
5. Produce a structured result.

Do not:

- start new architecture branches
- silently broaden scope
- mix unrelated fixes into one patch
- change backend semantics in UI-only tasks

## 5. Expected Delivery Format

Every delegated task must return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

If blocked, return:

- blocker
- what was attempted
- what is missing

## 6. Role Files

Use the role files in:

- [D:\code\MyAttention\.qoder\agents\coding-agent.md](/D:/code/MyAttention/.qoder/agents/coding-agent.md)
- [D:\code\MyAttention\.qoder\agents\code-review-agent.md](/D:/code/MyAttention/.qoder/agents/code-review-agent.md)
- [D:\code\MyAttention\.qoder\agents\test-fixer-agent.md](/D:/code/MyAttention/.qoder/agents/test-fixer-agent.md)
- [D:\code\MyAttention\.qoder\agents\refactor-agent.md](/D:/code/MyAttention/.qoder/agents/refactor-agent.md)
- [D:\code\MyAttention\.qoder\agents\architect-agent.md](/D:/code/MyAttention/.qoder/agents/architect-agent.md)
- [D:\code\MyAttention\.openclaw\agents\openclaw-glm-coding-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-glm-coding-agent.md)
- [D:\code\MyAttention\.openclaw\agents\openclaw-kimi-review-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-kimi-review-agent.md)

Pick the narrowest role that matches the task.

## 7. Review Gate

No delegated task is final until reviewed by the main controller.

Default acceptance policy:

- missing validation -> `accept_with_changes` or `reject`
- broadened scope -> `reject`
- strategy drift -> `reject`
- bounded patch with evidence -> eligible for acceptance
