# IKE Repository Rename P2-D11 Notification Visible Identity Result

## Scope

Normalize user-visible notification test and source labels from `MyAttention` to `IKE` without touching compatibility-sensitive runtime names, environment variables, database identifiers, or collection names.

## Files Changed

- [D:\code\MyAttention\services\web\components\settings\notifications-config.tsx](/D:/code/MyAttention/services/web/components/settings/notifications-config.tsx)
- [D:\code\MyAttention\services\api\routers\settings.py](/D:/code/MyAttention/services/api/routers/settings.py)
- [D:\code\MyAttention\services\api\notifications\task_notification.py](/D:/code/MyAttention/services/api/notifications/task_notification.py)
- [D:\code\MyAttention\services\api\notifications\dingtalk.py](/D:/code/MyAttention/services/api/notifications/dingtalk.py)
- [D:\code\MyAttention\services\api\notifications\feishu.py](/D:/code/MyAttention/services/api/notifications/feishu.py)

## What Changed

- Notification settings test action now sends `这是一条来自 IKE 的测试消息`.
- Backend notification test defaults now use:
  - `🔔 IKE 连接测试消息`
  - `🔔 IKE 通知测试 - 连接成功!`
  - `🔔 IKE 飞书通知测试`
  - `打开 IKE`
- Legacy task notification source label now uses `IKE 任务系统`.
- DingTalk / Feishu notification helpers now also use `IKE` in visible test titles and daily-digest footer text.

## Validation

```powershell
python -m compileall D:\code\MyAttention\services\api\routers\settings.py D:\code\MyAttention\services\api\notifications\task_notification.py D:\code\MyAttention\services\api\notifications\dingtalk.py D:\code\MyAttention\services\api\notifications\feishu.py
npx tsc --noEmit
```

## Recommendation

`accept_with_changes`

## Known Risks

- This patch only normalizes user-visible notification identity.
- Compatibility-sensitive `MyAttention` markers in env vars, database names, service names, loggers, and knowledge-store identifiers remain intentionally unchanged.
