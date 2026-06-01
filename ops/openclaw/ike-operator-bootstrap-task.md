# OpenClaw IKE Operator Bootstrap Task

Agent id: `ike-operator`

## Objective

Run a bounded runtime readiness check without repair.

## Required Reads

- `D:\code\_agent-runtimes\openclaw-workspaces\ike-operator\skills\ike-operator\SKILL.md`
- `D:\code\MyAttention\ops\state\current_state.json`
- `D:\code\MyAttention\ops\agents\openclaw-ike-operator.md`
- `D:\code\MyAttention\docs\RUNTIME_OPERATOR_LOOP_PROTOCOL_2026-05-09.md`

## Allowed Commands

```powershell
cd D:\code\MyAttention
python manage.py health --json
python manage.py status --json
```

Optional route probes if health says API/Web are healthy:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3002/chat
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3002/evolution
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3002/control
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
```

## Allowed Write

- `D:\code\MyAttention\tasks\codex\openclaw_ike_operator_runtime_readiness_result_2026-05-20.md`

## Forbidden

- no source edits
- no service start/stop in this bootstrap task
- no runtime config edits
- no promotion decisions

## Stop Condition

Stop after writing the readiness result or reporting why it is blocked.
