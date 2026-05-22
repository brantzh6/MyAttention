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

## 3. Lifecycle Governance

Adopt the `AgentSDLC` lifecycle shape as the project-level delivery contract:

1. Design
2. Design Review
3. Code Implementation
4. Code Review
5. Testing
6. Promotion Decision
7. Runtime Monitoring / Feedback

Rules:

- No non-trivial task skips Design or Design Review.
- No delegated task skips Code Review or Testing.
- No delegate decides promotion.
- Runtime signals feed back into new design work, not direct hot edits by default.
- Keep pipeline discipline:
  - max 3 active implementation/review nodes
  - max 1 active promotion-style decision node

Default project classification:

- Project Level: `L2` persistent personal system
- Project Type: `C` AI agent / workflow system
- Default Risk: `R2`
- Default Template: `T2`

Automatic escalation to `R3` / reinforced governance when a task touches:

- memory / persistence
- task orchestration or scheduler logic
- worker / harness execution contracts
- runtime truth or promotion boundaries
- permissions, deletion, or self-modification rules
- production incident remediation

## 4. Delegation And Model Routing

Default controller rule:

- controller coordinates lifecycle, writes briefs, and makes gate decisions
- delegates implement, review, and validate
- controller does not use direct coding as the default path

Default delegated lanes:

1. General coding
   - primary: `claude-worker + glm-5`
   - backup: `claude-worker + glm-5.1`
   - fallback: `openclaw + glm-5`
2. Critical coding
   - primary: `claude-worker + glm-5.1`
   - backup: `claude-worker + glm-5`
3. Frontend / UI / multimodal implementation
   - primary: `claude-worker + qwen3.6-plus`
   - backup: `claude-worker + glm-5`
4. Code review
   - primary: `claude-worker + kimi-k2.5`
   - backup: `openclaw + kimi-k2.5`
   - secondary backup: `claude-worker + glm-5`
5. Default testing
   - primary: `claude-worker + glm-5`
   - backup: `claude-worker + qwen3.6-plus` for GUI / frontend flows
6. Test scaffolding / bulk test patching
   - primary: `claude-worker + MiniMax-M2.5`
7. High-risk test strategy or hard validation diagnosis
   - primary: `claude-worker + glm-5.1`

Governance-health defaults:

- review files must have one canonical identity
- avoid opening new review nodes while old ones are still ambiguous
- treat review-file drift as a controller governance problem, not a reviewer problem

Execution defaults:

- prefer `one_shot` bounded tasks
- use `detached` only when the packet is long-running but still single-result
- do not use `continue` as the default development lane
- every coding, review, and test packet should be independently auditable

## 5. Architectural Corrections Already Made

These are not optional preferences. Do not regress them.

1. Source value is contextual.
   - A source such as `36kr` is not globally good or bad.
   - Value depends on task intent and role in context.

2. `topic -> source` is not the long-term model.
   - Prefer `object + task intent + role in context`.

3. Evolution brain is not the watchdog.
   - Watchdog/rule layer keeps runtime alive.
   - Evolution layer should increasingly perform model-assisted prioritization and diagnosis.

## 6. Safe Working Pattern

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

## 7. Expected Delivery Format

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

## 8. Role Files

Use the role files in:

- [D:\code\MyAttention\.qoder\agents\coding-agent.md](/D:/code/MyAttention/.qoder/agents/coding-agent.md)
- [D:\code\MyAttention\.qoder\agents\code-review-agent.md](/D:/code/MyAttention/.qoder/agents/code-review-agent.md)
- [D:\code\MyAttention\.qoder\agents\test-fixer-agent.md](/D:/code/MyAttention/.qoder/agents/test-fixer-agent.md)
- [D:\code\MyAttention\.qoder\agents\refactor-agent.md](/D:/code/MyAttention/.qoder/agents/refactor-agent.md)
- [D:\code\MyAttention\.qoder\agents\architect-agent.md](/D:/code/MyAttention/.qoder/agents/architect-agent.md)
- [D:\code\MyAttention\.openclaw\agents\openclaw-glm-coding-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-glm-coding-agent.md)
- [D:\code\MyAttention\.openclaw\agents\openclaw-kimi-review-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-kimi-review-agent.md)

Pick the narrowest role that matches the task.

## 9. Review Gate

No delegated task is final until reviewed by the main controller.

Default acceptance policy:

- missing validation -> `accept_with_changes` or `reject`
- broadened scope -> `reject`
- strategy drift -> `reject`
- bounded patch with evidence -> eligible for acceptance

## 10. Governance Reference

Do not hardcode evolving governance procedures in this file.

Instead, apply the current project governance framework and its linked indices:

- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- [D:\code\MyAttention\docs\IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md](/D:/code/MyAttention/docs/IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md)
- [D:\code\MyAttention\docs\CHANGE_MANAGEMENT.md](/D:/code/MyAttention/docs/CHANGE_MANAGEMENT.md)
- [D:\code\MyAttention\docs\VERSION_MANAGEMENT.md](/D:/code/MyAttention/docs/VERSION_MANAGEMENT.md)

This file should define working boundaries and controller duties, while the governance docs define the current operating procedure.
