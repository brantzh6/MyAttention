# IKE Repository Rename Reference Inventory

Date: 2026-04-09

## Purpose

This note records the first practical inventory of cutover blockers after the parallel clean root was created.

The blocker is no longer:

- dirty parallel root contents

The blocker is now:

- historical `MyAttention`
- historical `D:\code\MyAttention`
- service/unit names and route assumptions that still encode the old identity

## Truthful Scope

This is not a full line-by-line rewrite list.

It is a controller inventory of the major categories that still need normalization before a final controller cutover to:

- `D:\code\IKE`

## Major Reference Buckets

### 1. Runtime / app code references

Examples appeared in:

- `services/api/config.py`
- `services/api/main.py`
- `services/api/run_service.py`
- `services/api/feeds/ai_tester.py`
- `services/api/feeds/external_agent.py`
- `services/api/feeds/fetcher.py`
- `services/api/llm/adapter.py`
- `services/api/llm/voting.py`
- `services/api/notifications/*.py`
- `services/api/routers/chat.py`
- `services/api/routers/feeds.py`
- `services/api/routers/feishu.py`
- `services/api/routers/settings.py`
- `services/api/routers/system.py`

These need a later narrow pass to distinguish:

- true project identity strings
- file-system root assumptions
- user-facing labels

### 2. Frontend references

Examples appeared in:

- `services/web/app/layout.tsx`
- `services/web/components/chat/chat-interface.tsx`
- `services/web/components/settings/ike-workspace-manager.tsx`
- `services/web/components/settings/notifications-config.tsx`
- `services/web/components/ui/sidebar.tsx`

These likely contain a mix of:

- branding text
- settings text
- path assumptions

### 3. Delegation / controller scripts

Examples appeared in:

- `scripts/acpx/openclaw_delegate.py`
- `scripts/qoder/create_review_bundle.py`
- `scripts/qoder/create_task_bundle.py`
- `scripts/qoder/qoder_delegate.py`
- `scripts/sync_isolated_workspaces.ps1`

These are high-value rename targets because they affect:

- automation
- delegation roots
- path routing

### 4. Service deployment artifacts

Examples appeared in:

- `scripts/services/windows/install-app-services.ps1`
- `scripts/services/windows/winsw/MyAttentionApi.xml`
- `scripts/services/windows/winsw/MyAttentionWatchdog.xml`
- `scripts/services/windows/winsw/MyAttentionWeb.xml`
- `scripts/services/linux/myattention-api.service`
- `scripts/services/linux/myattention-watchdog.service`
- `scripts/services/macos/com.myattention.api.plist`
- `scripts/services/macos/com.myattention.watchdog.plist`

This bucket is especially important because rename errors here will directly affect:

- service names
- launch commands
- controller live proof assumptions

### 5. Local runtime config

Examples appeared in:

- `config/runtime/local-process.local.example.toml`
- `config/runtime/local-process.local.toml`
- `infrastructure/docker-compose.yml`

These need a narrow pass because they can encode:

- repository root assumptions
- service names
- container/project names

## Excluded Noise

The raw search also hit many non-actionable files such as:

- `__pycache__`
- runtime logs
- test caches

Those are not rename blockers and should not be treated as migration work items.

## Controller Judgment

The repository restructure is now in this truthful state:

- clean parallel root:
  - materially done
- workspace isolation:
  - materially done
- final rename/cutover:
  - blocked on hardcoded reference normalization

## Next Best Step

Do not attempt one giant rename sweep.

Instead, split the normalization into narrow packets:

1. service/deployment artifacts
2. local runtime config
3. controller/delegation scripts
4. runtime/backend identity references
5. frontend branding/path references
