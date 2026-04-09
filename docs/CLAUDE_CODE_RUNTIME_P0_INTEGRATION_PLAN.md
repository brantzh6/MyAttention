# Claude Code Runtime P0 Integration Plan

## 1. Goal

Establish Claude Code as a **local execution substrate** for delegated work,
without giving it controller responsibility.

This P0 is only to prove:

- local coding lane works
- local review lane works
- run artifacts are durable
- Codex/controller can review outputs
- the success path is auditable from local artifacts alone

It is **not** to replace `IKE Runtime`.
It is **not** to make Claude Code the top-level planner.

## 2. Required Positioning

Claude Code in this phase is:

- a local worker runtime
- a bounded coding/review execution lane
- subordinate to controller task packets and acceptance

Claude Code in this phase is **not**:

- the main controller
- the memory system
- the task-truth system
- the decision authority

## 3. P0 Scope

P0 should deliver exactly these capabilities:

1. `claude-coder` lane
- accept one bounded coding packet
- execute locally
- return durable structured result

2. `claude-reviewer` lane
- accept one bounded review packet
- execute locally
- return durable structured result

3. durable run storage
- one run directory per task
- stable metadata
- stable final result
- stable events/log capture

4. worker package usability
- the worker package can be built and run locally
- the local `claude` command can be invoked from this machine
- the happy path does not require OpenClaw transport

5. controller compatibility
- output is reviewable by current project harness
- result schema can be mapped into current controller expectations

## 4. Non-Goals

Do **not** do these in P0:

- do not make Claude Code the controller
- do not design long-term memory here
- do not design task state truth here
- do not build broad multi-agent orchestration
- do not replace `IKE Runtime v0`
- do not build UI
- do not solve every resume/streaming/worktree feature first

## 5. Implementation Requirements

### A. Runtime substrate

The implementation must use:

- standard Claude Code CLI or supported local Claude runtime
- default model is `glm-5` unless explicitly overridden

Do **not**:

- build on leaked Claude Code source
- fork Claude internals
- depend on OpenClaw transport

Model selection must be explicit and local:

- launch-time override: `claude --model <model_name>`
- in-session override: `/model <model_name>`
- the worker package should preserve the selected model in durable run
  metadata

### B. Tool surface

Keep the tool surface small and high-level.

Minimum operations:

- start coding task
- wait for run
- fetch artifacts
- abort run

Optional in P0:

- continue/resume

### C. Result durability

Each run must write durable local artifacts, for example:

- `meta.json`
- `events.ndjson`
- `final.json`
- `summary.md`
- `patch.diff`

Artifact locations must be stable enough that a completed run can be re-read
after process exit without chat history.
The selected Claude model must also be recorded in `meta.json` or equivalent
run metadata.

### D. Harness compatibility

The worker result must be mappable to current project coding/review contracts.

Coding result must be convertible into:

- `summary`
- `files_changed`
- `validation_run`
- `known_risks`
- `recommendation`

Review result must be convertible into:

- `findings` or `top_findings`
- `validation_gaps`
- `recommendation`

### E. Required worker report

The worker session must return a controller-readable report containing:

1. what changed
2. exact file paths
3. exact run command(s)
4. artifact paths
5. one toy-run proof
6. one real bounded-packet proof
7. current gaps
8. recommendation: `accept`, `accept_with_changes`, or `reject`

## 6. Suggested Execution Order

1. verify local Claude CLI is installed and callable
2. build the worker package
3. run one toy coding task in a throwaway repo
4. verify durable artifacts are written
5. run one toy review task
6. add result-schema adapter if needed
7. run one real bounded project packet

## 7. Recommended First Real Packet

Use one **narrow project packet** only after toy proof succeeds.

Recommended first real task type:

- bounded backend/runtime coding packet

Recommended first real review type:

- bounded runtime review packet

Do **not** start with:

- UI-heavy work
- architecture tasks
- benchmark/evolution tasks

## 8. Acceptance Criteria

P0 is accepted only if **all** of the following are true:

### Environment

1. local `claude` command is available
2. local auth works
3. package builds successfully

### Coding lane

4. one toy coding task completes end-to-end
5. one real bounded coding packet completes end-to-end
6. changed files are recoverable from artifacts
7. validation command/output is durably recorded

### Review lane

8. one toy review task completes end-to-end
9. one real bounded review packet completes end-to-end
10. review result is durably recorded and controller-readable

### Durability

11. each run has durable local artifacts on disk
12. a completed run can be re-read after process exit
13. controller can inspect final result without relying on chat history

### Boundary integrity

14. Claude Code never becomes controller in the workflow
15. architecture/priority/acceptance remain outside the worker
16. no OpenClaw transport is required for the successful P0 path

## 9. Rejection Conditions

Reject P0 if any of these happen:

- only toy tasks work, but no real bounded project packet works
- result durability depends on chat output rather than local artifacts
- worker result cannot be mapped into current harness expectations
- Claude Code is implicitly acting as planner/controller
- setup still secretly depends on OpenClaw transport to be usable

## 10. Handoff Back To Controller

When the separate session finishes, it should return:

1. what was built
2. exact file paths
3. exact run command(s)
4. exact artifact paths
5. toy coding proof
6. toy review proof
7. real bounded coding packet proof
8. real bounded review packet proof
9. current gaps
10. recommendation:
   - `accept`
   - `accept_with_changes`
   - `reject`

## 11. Controller Judgment

If P0 succeeds, Claude Code should become:

- a new local bounded coding/review substrate

It should still remain:

- below controller
- below runtime truth
- below task/decision/memory governance
