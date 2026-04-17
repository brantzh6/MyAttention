# IKE Repository Rename Compatibility Remainder

Date: 2026-04-09
Status: accept_with_changes

## Purpose

Separate remaining `MyAttention` references into:

1. safe to rename now
2. compatibility-sensitive, keep for now
3. broader product rename items, defer

## Keep For Now: Compatibility-Sensitive

These should not be renamed in the same narrow pass without a broader migration:

### Infra/service compatibility

- `config/runtime/local-process.local.toml`
  - `MyAttentionPostgres`
  - `MyAttentionRedis`
- `config/runtime/local-process.local.example.toml`
  - commented infra examples
- `services/api/routers/system.py`
  - legacy alias support for `myattention-*`
- `services/api/tests/test_system_runtime_identity.py`
  - tests that verify legacy alias compatibility
- `scripts/services/windows/README.md`
  - examples for current local infra service names

### Storage / namespace compatibility

- `services/api/memory/engine.py`
  - `myattention_memories`
- `services/api/rag/engine.py`
  - `myattention_docs`
- browser/local cache namespace:
  - `services/web/lib/feed-cache.ts`
  - `services/web/components/chat/chat-interface.tsx`

### Environment variable compatibility

- `MYATTENTION_*` environment variables in:
  - `services/api/pipeline/scheduler.py`
  - `services/api/feeds/log_monitor.py`
  - `services/api/feeds/task_processor.py`

## Defer: Broader Product/Feature Rename

These are real product-surface rename items, but not narrow cutover blockers.
Some of the earlier visible-string backlog has already been reduced by narrow packets; the remaining examples below are intentionally broader or lower priority.

- feed/external-agent legacy product naming
- comments/docstrings that mention the old product name but do not affect runtime behavior
- older test/demo data

Already materially normalized in narrow packets:

- chat assistant prompt text
- notification titles/messages
- Feishu/notification UI strings

Still defer:

- feed/external-agent legacy product naming
- older test/demo data

Examples:

- `services/api/routers/feishu.py`
- `services/api/feeds/external_agent.py`
- `services/api/routers/feeds.py`

## Safe To Continue Renaming In Narrow Packets

- visible IKE runtime surface labels
- metadata/browser title
- package/workspace identity
- repo-root assumptions in tests
- service/deployment templates
- controller/delegation docs and plans

## Controller Judgment

The rename stream should continue, but only by preserving this split:

- compatibility-sensitive identifiers stay until explicit migration
- visible/runtime/controller identities continue moving to `IKE`

Do not flatten all remaining `MyAttention` references into one broad rename task.
