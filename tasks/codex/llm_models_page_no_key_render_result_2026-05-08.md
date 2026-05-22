# LLM Models Page No-Key Render Result

Date: 2026-05-08

Task ID: LLM_MODELS_PAGE_NO_KEY_RENDER_P0_2026-05-08

Recommendation: accept

## Summary

Fixed the `/settings/models` UI so it renders normally even when no API keys are configured.

The page now:

- shows a static provider catalog immediately
- syncs live provider status in the background
- keeps provider cards visible even when keys are missing
- treats keys as runtime activation data, not as a prerequisite for the page

## Files Changed

- `services/web/components/settings/models-config.tsx`

## Why This Solution

The previous version waited on live provider status before presenting a useful page. That made the main configuration UI feel key-dependent. The new version uses a static provider catalog as the default render path and overlays live status only when available.

This matches the operational requirement that normal UI should not assume a key exists.

## Validation Run

```powershell
cd services/web
npm run build
```

Result:

```text
passed
```

Browser smoke:

```text
title: IKE - 信息大脑、知识大脑、进化大脑、世界模型与思维工具
inputCount: 9
buttonCount: 19
snippet: provider cards visible, no key required for render
errors: []
```

## Known Risks

- Live provider sync can still reflect backend state when it is available, but the page no longer blocks on it.
- This is still a settings surface, not the main product loop. It should stay visually clear but operationally secondary.

## Recommendation

accept
