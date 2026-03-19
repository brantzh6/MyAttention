"""
Pipeline Scheduler - Runs info collection pipeline on configurable intervals.
Integrates into FastAPI lifespan as a background asyncio task.
"""

import asyncio
import importlib
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from notifications import get_notification_manager, NotificationChannel

log = logging.getLogger("pipeline")

DEFAULT_SKILLS_DIRS = [
    Path(os.environ["MYATTENTION_SKILLS_DIR"]).expanduser()
    for _ in [0]
    if os.environ.get("MYATTENTION_SKILLS_DIR")
]
if os.environ.get("CODEX_HOME"):
    DEFAULT_SKILLS_DIRS.append(Path(os.environ["CODEX_HOME"]).expanduser() / "skills")
DEFAULT_SKILLS_DIRS.append(Path.home() / ".codex" / "skills")


class PipelineScheduler:
    """
    Background scheduler for the info-gathering pipeline.

    Designed to run inside FastAPI lifespan:

        scheduler = PipelineScheduler(api_base="http://localhost:8000")
        task = asyncio.create_task(scheduler.run())
        yield
        scheduler.stop()
        await task
    """

    def __init__(
        self,
        api_base: str = "http://localhost:8000",
        high_priority_interval: int = 300,    # 5 min
        full_interval: int = 1800,            # 30 min
        urgency_threshold: float = 0.7,
        enabled: bool = True,
        digest_times: list = None,            # ["09:00", "18:00"]
    ):
        self.api_base = api_base
        self.high_priority_interval = high_priority_interval
        self.full_interval = full_interval
        self.urgency_threshold = urgency_threshold
        self.enabled = enabled
        self.digest_times = digest_times or ["09:00", "18:00"]
        self._running = False
        self._last_high = 0.0
        self._last_full = 0.0
        self._last_digest_hour = -1  # Track last digest hour
        self._stats = {
            "total_runs": 0,
            "total_items": 0,
            "total_imported": 0,
            "last_run_at": None,
            "errors": 0,
            "digests_sent": 0,
        }

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def stop(self):
        log.info("Pipeline scheduler stopping...")
        self._running = False

    def _resolve_skill_dir(self, skill_name: str) -> Path | None:
        for base_dir in DEFAULT_SKILLS_DIRS:
            candidate = base_dir / skill_name
            if candidate.exists():
                return candidate
        return None

    def _load_skill_module(self, skill_name: str, module_name: str):
        import sys

        skill_dir = self._resolve_skill_dir(skill_name)
        if skill_dir is None:
            return None

        skill_path = str(skill_dir)
        if skill_path not in sys.path:
            sys.path.insert(0, skill_path)

        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            return None

    async def _fallback_gather(self, priority: str = "all", limit: int = 20) -> dict[str, Any]:
        from feeds.fetcher import get_feed_fetcher

        fetcher = get_feed_fetcher()
        entries = await fetcher.fetch_all(limit_per_source=max(limit, 5))

        if priority == "high":
            entries = [entry for entry in entries if entry.importance >= self.urgency_threshold]

        entries = entries[:limit]
        items = [
            {
                "id": entry.id,
                "title": entry.title,
                "link": entry.url,
                "url": entry.url,
                "summary": entry.summary,
                "content": entry.summary,
                "source": entry.source_id,
                "source_name": entry.source_name,
                "source_type": "rss",
                "category": entry.category,
                "category_name": entry.category,
                "secondary_tags": [],
                "urgency": entry.importance,
                "urgency_factors": {},
                "language": "zh",
                "published_at": entry.published_at.isoformat(),
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "pipeline": "local_fallback",
                },
            }
            for entry in entries
        ]
        return {
            "items": items,
            "stats": {
                "items_collected": len(items),
                "mode": "local_fallback",
            },
        }

    def _fallback_process(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        items = raw_data.get("items", [])
        return {
            "status": "ok" if items else "empty",
            "items": items,
            "stats": {
                "total_processed": len(items),
                "mode": raw_data.get("stats", {}).get("mode", "local_fallback"),
            },
        }

    async def _gather(self, priority: str = "all", limit: int = 20) -> dict:
        """Run info-gatherer and return raw items."""
        module = self._load_skill_module("info-gatherer", "gatherer")
        if module and hasattr(module, "gather"):
            return await module.gather(priority=priority, limit=limit)

        log.warning("info-gatherer skill not found, using local fallback gatherer")
        return await self._fallback_gather(priority=priority, limit=limit)

    def _process(self, raw_data: dict) -> dict:
        """Run info-processor on gathered data."""
        items = raw_data.get("items", [])
        if not items:
            return {"status": "empty", "items": [], "stats": {}}

        module = self._load_skill_module("info-processor", "processor")
        if module and hasattr(module, "InfoProcessor"):
            processor = module.InfoProcessor(summary_length=200)
            return processor.process_batch(items)

        log.warning("info-processor skill not found, using local fallback processor")
        return self._fallback_process(raw_data)

    async def _import_to_api(self, processed: dict) -> dict:
        """POST processed items to /api/feeds/import."""
        import aiohttp

        items = processed.get("items", [])
        if not items:
            return {"imported": 0, "duplicates": 0}

        url = f"{self.api_base}/api/feeds/import"
        payload = {"items": items, "stats": processed.get("stats", {})}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        log.error(f"Import failed: HTTP {resp.status}")
                        return {"imported": 0, "error": f"HTTP {resp.status}"}
        except Exception as e:
            log.error(f"Import error: {e}")
            return {"imported": 0, "error": str(e)}

    async def _push_urgent(self, processed: dict) -> dict:
        """Push urgent items to configured notification channels."""
        items = processed.get("items", [])
        urgent = [i for i in items if i.get("urgency", 0) >= self.urgency_threshold]

        if not urgent:
            return {"pushed": 0}

        pushed = 0
        manager = get_notification_manager()

        for item in urgent[:5]:  # 最多推送5条紧急新闻
            title = item.get("title", "重要新闻")
            source = item.get("source", "未知来源")
            summary = item.get("summary", item.get("content", ""))[:200]
            url = item.get("url", "")
            urgency = item.get("urgency", 0.7)

            try:
                results = await manager.send_news_card(
                    title=title,
                    source=source,
                    summary=summary,
                    url=url,
                    urgency=urgency
                )
                if any(results.values()):
                    pushed += 1
                    log.info(f"Pushed urgent: {title}")
            except Exception as e:
                log.error(f"Failed to push {title}: {e}")

        return {"pushed": pushed}

    async def _send_digest(self, digest_type: str = "daily") -> dict:
        """Send scheduled digest to notification channels."""
        import aiohttp

        try:
            # Fetch recent items from API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/api/feeds",
                    params={"limit": 20},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        return {"sent": False, "error": f"HTTP {resp.status}"}
                    data = await resp.json()

            items = data if isinstance(data, list) else data.get("items", [])
            if not items:
                return {"sent": False, "error": "No items"}

            manager = get_notification_manager()

            if digest_type == "morning":
                results = await manager.send_morning_brief(items)
            elif digest_type == "evening":
                results = await manager.send_evening_brief(items)
            else:
                results = await manager.send_daily_digest(items)

            success = any(results.values())
            if success:
                self._stats["digests_sent"] += 1
                log.info(f"Digest sent: {digest_type}")

            return {"sent": success, "results": results}

        except Exception as e:
            log.error(f"Failed to send digest: {e}")
            return {"sent": False, "error": str(e)}

    async def run_once(self, priority: str = "all", push: bool = True) -> dict[str, Any]:
        """Execute the full pipeline once."""
        start = time.time()
        log.info(f"Pipeline run: priority={priority}")

        try:
            # Step 1: Gather
            raw = await self._gather(priority=priority)
            gathered = raw.get("stats", {}).get("items_collected", 0)

            # Step 2: Process
            processed = self._process(raw)
            proc_stats = processed.get("stats", {})

            # Step 3: Import
            import_result = await self._import_to_api(processed)
            imported = import_result.get("imported", 0)

            # Step 4: Push urgent
            push_result = {"pushed": 0}
            if push:
                push_result = await self._push_urgent(processed)

            elapsed = round(time.time() - start, 1)

            # Update stats
            self._stats["total_runs"] += 1
            self._stats["total_items"] += gathered
            self._stats["total_imported"] += imported
            self._stats["last_run_at"] = datetime.now(timezone.utc).isoformat()

            log.info(
                f"Pipeline done in {elapsed}s: "
                f"gathered={gathered}, processed={proc_stats.get('total_processed', 0)}, "
                f"imported={imported}, pushed={push_result.get('pushed', 0)}"
            )

            return {
                "elapsed": elapsed,
                "gathered": gathered,
                "processed": proc_stats.get("total_processed", 0),
                "imported": imported,
                "pushed": push_result.get("pushed", 0),
            }

        except Exception as e:
            self._stats["errors"] += 1
            log.error(f"Pipeline error: {e}", exc_info=True)
            return {"error": str(e)}

    async def run(self):
        """Main scheduler loop - call this as an asyncio task."""
        self._running = True
        log.info(
            f"Pipeline scheduler started "
            f"(high={self.high_priority_interval}s, full={self.full_interval}s, "
            f"digest_times={self.digest_times})"
        )

        # Wait a few seconds for the API to fully start
        await asyncio.sleep(5)

        # Initial full collection
        await self.run_once(priority="all", push=True)
        now = time.time()
        self._last_high = now
        self._last_full = now

        while self._running:
            try:
                now = time.time()
                now_dt = datetime.now()

                # Check for digest time
                current_hour_minute = now_dt.strftime("%H:%M")
                current_hour = now_dt.hour

                for digest_time in self.digest_times:
                    if (current_hour_minute == digest_time and
                        current_hour != self._last_digest_hour):
                        # Determine digest type
                        hour = int(digest_time.split(":")[0])
                        if 6 <= hour < 12:
                            digest_type = "morning"
                        elif 17 <= hour < 21:
                            digest_type = "evening"
                        else:
                            digest_type = "daily"

                        await self._send_digest(digest_type)
                        self._last_digest_hour = current_hour

                # Regular collection intervals
                if now - self._last_full >= self.full_interval:
                    await self.run_once(priority="all", push=True)
                    self._last_full = now
                    self._last_high = now
                elif now - self._last_high >= self.high_priority_interval:
                    await self.run_once(priority="high", push=True)
                    self._last_high = now

                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)

        log.info("Pipeline scheduler stopped.")
