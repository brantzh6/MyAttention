# Windows 服务模板

用于 MyAttention 在 Windows 环境下的服务化运行说明。

当前建议：

- PostgreSQL：使用 `pg_ctl register`
- Redis：使用 `redis-server --service-install`
- API / Web / Watchdog：建议使用 NSSM 或专门的 Windows Service 包装

当前本机已采用的服务名：

- `MyAttentionPostgres`
- `MyAttentionRedis`

应用层推荐服务名：

- `MyAttentionApi`
- `MyAttentionWeb`
- `MyAttentionWatchdog`

示例注册命令：

```powershell
D:\tools\postgresql17\pgsql\bin\pg_ctl.exe register `
  -N MyAttentionPostgres `
  -D D:\tools\postgres-data `
  -S demand

D:\tools\redis\Redis-x64-5.0.14.1\redis-server.exe `
  --service-install D:\tools\redis\redis.local.conf `
  --service-name MyAttentionRedis
```

常用操作：

```powershell
sc.exe start MyAttentionPostgres
sc.exe start MyAttentionRedis
sc.exe stop MyAttentionPostgres
sc.exe stop MyAttentionRedis
```

应用层模板脚本：

- `install-app-services.ps1`
- `uninstall-app-services.ps1`

WinSW XML 模板：

- `winsw/MyAttentionApi.xml`
- `winsw/MyAttentionWeb.xml`
- `winsw/MyAttentionWatchdog.xml`

说明：

- 这两个脚本默认使用 `NSSM`
- 不会自动执行
- 需要先确认 `.venv`、Next standalone 产物和日志目录已准备好
