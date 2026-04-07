# Qoder Automation Workflow

Use this workflow when the main controller wants qoder to take a bounded task without manual task rewriting.

## 1. Create an implementation bundle

Use:

`D:\code\MyAttention\scripts\qoder\create_task_bundle.py`

Outputs:

- brief file
- context file
- result file
- done signal file
- launch command

## 2. Launch the implementation bundle

Use:

`D:\code\MyAttention\scripts\qoder\launch_bundle.py`

with the bundle JSON captured from step 1.

## 3. Watch for completion

Use:

`D:\code\MyAttention\scripts\qoder\watch_result.py`

This checks:

- whether the declared result file is fully populated
- whether qoder wrote the `done.json` completion signal

If it times out or the files are still incomplete, the delegation is still `pending_or_blocked`.

## 4. Qoder writes back

Qoder must write:

- the result into the declared result file
- a completion signal into the declared done file
- one bounded commit

Required result sections:

- Summary
- Files Changed
- Commit Hash
- Validation Run
- Known Risks
- Recommendation

Required done signal fields:

- `task_id`
- `status`
- `result_file`
- `commit_hash`
- `timestamp`

## 5. Create a review bundle

Use:

`D:\code\MyAttention\scripts\qoder\create_review_bundle.py`

Inputs:

- target brief
- target result
- changed files

## 6. Launch the review bundle

Again use:

`D:\code\MyAttention\scripts\qoder\launch_bundle.py`

## 7. Main controller review

Main controller still decides:

- accept
- accept_with_changes
- reject

## Notes

- This is still file-based delegation.
- `done.json` is the primary completion signal; the result file is the primary review artifact.
- Qoder is the lightweight execution lane.
- OpenClaw remains useful for multi-agent analysis and challenge/review workflows.
- If you want the shortest path, use `D:\code\MyAttention\scripts\qoder\run_task.py` as the single-command create + launch + watch flow.
