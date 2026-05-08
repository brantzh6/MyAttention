# LLM Local Secret Config Result

Date: 2026-05-08

Task ID: LLM_LOCAL_SECRET_CONFIG_P0_2026-05-08

Recommendation: accept

## Summary

Added a reusable local configuration path for LLM API keys.

The project no longer requires one-off shell environment variables for local Qwen setup. Operators can use the UI at:

```text
/settings/models
```

to save provider keys into a gitignored local runtime secret file:

```text
.runtime/secrets/llm.local.env
```

Environment variables still take precedence over the local secret file.

## Files Changed

- `services/api/config.py`
- `services/api/routers/models.py`
- `services/web/lib/api-client.ts`
- `services/web/components/settings/models-config.tsx`

## Boundary

- API keys are not committed.
- API keys are not echoed back through the API.
- The local secret file is under `.runtime/`, which is already gitignored.
- This does not create runtime truth, memory, promotion state, or model routing policy changes.

## Validation Run

```powershell
python -m py_compile services/api/config.py services/api/routers/models.py
```

Result:

```text
passed
```

```powershell
cd services/web
npm run build
```

Result:

```text
passed
```

## Known Risks

- The local secret file is a local developer secret store, not a cross-machine secret manager.
- On Windows, `chmod 0600` is best-effort only; machine-level credential vault integration remains a future hardening option.
- Existing API processes must run the new code before `/settings/models` can save keys.

## Next Action

Restart the API service, save the Qwen key from `/settings/models`, then rerun the real Flywheel controller rehearsal.
