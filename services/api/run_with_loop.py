
import sys
import asyncio

# Windows 上使用 Selector 事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 启动 uvicorn
import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
