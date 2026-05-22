# IKE Runtime v0 Packet R1-F3 Test Brief

## Task ID

- `R1-F3`

## Goal

Independently validate the `R1-F1` controller-facing runtime read surface.

## Required focus

At minimum verify:

1. current project read output follows `RuntimeProject.current_work_context_id`
2. active/waiting task visibility is derived from runtime truth
3. latest finalized decision / trusted packets are included truthfully
4. missing upstream truth does not get invented in the read output

## Required output

- `scenarios_run`
- `pass_fail`
- `gaps_not_tested`
- `risks_remaining`
- `recommendation`
