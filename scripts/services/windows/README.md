# Windows Service Templates

Used for running IKE on Windows as services.

Current recommendation:

- PostgreSQL: use `pg_ctl register`
- Redis: use `redis-server --service-install`
- API / Web / Watchdog: use `NSSM` or a dedicated Windows service wrapper

Current local infrastructure service names:

- `MyAttentionPostgres`
- `MyAttentionRedis`

Current application-layer recommended service names:

- `IKEApi`
- `IKEWeb`
- `IKEWatchdog`

Example registration commands:

```powershell
D:\tools\postgresql17\pgsql\bin\pg_ctl.exe register `
  -N MyAttentionPostgres `
  -D D:\tools\postgres-data `
  -S demand

D:\tools\redis\Redis-x64-5.0.14.1\redis-server.exe `
  --service-install D:\tools\redis\redis.local.conf `
  --service-name MyAttentionRedis
```

Common operations:

```powershell
sc.exe start MyAttentionPostgres
sc.exe start MyAttentionRedis
sc.exe stop MyAttentionPostgres
sc.exe stop MyAttentionRedis
```

Application-layer install script:

- `install-app-services.ps1`
- `uninstall-app-services.ps1`

WinSW XML templates:

- `winsw/MyAttentionApi.xml`
- `winsw/MyAttentionWeb.xml`
- `winsw/MyAttentionWatchdog.xml`

Notes:

- the install script defaults to:
  - `RepoRoot = D:\code\IKE`
  - `ServicePrefix = IKE`
- the uninstall script defaults to:
  - `ServicePrefix = IKE`
- it does not execute automatically
- confirm `.venv`, Next standalone output, and log directories are ready before install
