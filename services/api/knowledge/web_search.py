"""
Web Search Integration - Aliyun IQS (Intelligent Query Service)

Provides web search capabilities using Aliyun IQS API.
Search results can be automatically indexed into knowledge bases.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib import request, error
import json
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import get_kb_manager, Document


@dataclass
class WebSearchResult:
    """Web search result"""
    title: str
    link: str
    snippet: str
    published_time: str = ""
    main_text: str = ""
    score: float = 0.0
    source: str = ""


class AliyunWebSearch:
    """
    Aliyun IQS (Intelligent Query Service) Web Search

    Features:
    - Unified search across multiple sources
    - Configurable time range and engine type
    - Automatic content extraction
    - Knowledge base integration
    """

    # Default API configuration
    DEFAULT_API_KEY = "D7axjMSTUzrfbP7g6NHCtjO1zOIViNah"
    DEFAULT_ENDPOINT = "https://cloud-iqs.aliyuncs.com/search/unified"

    # Engine types
    ENGINE_GENERIC = "Generic"           # General search
    ENGINE_ADVANCED = "GenericAdvanced"  # Advanced search with better ranking
    ENGINE_LITE = "LiteAdvanced"         # Lite version

    # Time ranges
    TIME_ONE_DAY = "OneDay"
    TIME_ONE_WEEK = "OneWeek"
    TIME_ONE_MONTH = "OneMonth"
    TIME_ONE_YEAR = "OneYear"
    TIME_NO_LIMIT = "NoLimit"

    def __init__(self):
        self.api_key = os.getenv("ALIYUN_IQS_API_KEY", self.DEFAULT_API_KEY)
        self.endpoint = os.getenv("ALIYUN_IQS_ENDPOINT", self.DEFAULT_ENDPOINT)

    def search(
        self,
        query: str,
        engine_type: str = "Generic",
        time_range: str = "NoLimit",
        main_text: bool = True,
        summary: bool = False,
        rerank_score: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform web search using Aliyun IQS API

        Args:
            query: Search query
            engine_type: Engine type (Generic/GenericAdvanced/LiteAdvanced)
            time_range: Time range filter
            main_text: Whether to fetch main text content
            summary: Whether to include AI summary (paid feature)
            rerank_score: Whether to include relevance score
            limit: Maximum results to return

        Returns:
            Search results with metadata
        """
        # Build request payload
        payload = {
            "query": query,
            "engineType": engine_type,
            "timeRange": time_range,
            "contents": {
                "mainText": main_text,
                "summary": summary,
                "rerankScore": rerank_score
            }
        }

        # Build request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            # Create and send request
            req = request.Request(
                self.endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )

            with request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self._format_results(data, limit)

        except error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.code}: {e.reason}",
                "details": e.read().decode('utf-8') if e.fp else None,
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    def _format_results(self, data: dict, limit: int) -> Dict[str, Any]:
        """Format API response into structured results"""
        # Check for errors
        if "error" in data or ("requestId" not in data and data.get("code") != 200):
            return {
                "success": False,
                "error": data.get("message", "Unknown error"),
                "results": []
            }

        # Extract results
        items = data.get("pageItems", [])
        results = []

        for item in items[:limit]:
            result = WebSearchResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                published_time=item.get("publishedTime", ""),
                main_text=item.get("mainText", ""),
                score=item.get("rerankScore", 0.0),
                source=self._extract_domain(item.get("link", ""))
            )
            results.append(result)

        return {
            "success": True,
            "total": len(results),
            "total_available": len(items),
            "query": data.get("query", ""),
            "engine_type": data.get("engineType", ""),
            "time_range": data.get("timeRange", ""),
            "results": results
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return url

    async def search_and_index(
        self,
        query: str,
        kb_id: str = "default",
        engine_type: str = "Generic",
        time_range: str = "NoLimit",
        min_score: float = 0.5,
        auto_index: bool = True
    ) -> Dict[str, Any]:
        """
        Search web and optionally index results to knowledge base

        Args:
            query: Search query
            kb_id: Knowledge base ID to store results
            engine_type: Search engine type
            time_range: Time range filter
            min_score: Minimum relevance score for indexing
            auto_index: Whether to automatically index results

        Returns:
            Search results and indexing status
        """
        # Perform search
        search_result = self.search(
            query=query,
            engine_type=engine_type,
            time_range=time_range,
            main_text=True,
            rerank_score=True
        )

        if not search_result.get("success"):
            return search_result

        if not auto_index:
            return search_result

        # Index results to knowledge base
        kb_manager = get_kb_manager()
        indexed_count = 0
        indexed_docs = []

        for result in search_result["results"]:
            # Skip low relevance results
            if result.score < min_score:
                continue

            # Use main text if available, otherwise use snippet
            content = result.main_text or result.snippet
            if not content:
                continue

            # Create document
            doc = Document(
                id=str(uuid.uuid4()),
                content=content,
                title=result.title,
                source=result.source,
                source_type="web_search",
                url=result.link,
                file_type="html",
                kb_id=kb_id,
                metadata={
                    "search_query": query,
                    "search_score": result.score,
                    "published_time": result.published_time,
                    "indexed_at": datetime.now().isoformat(),
                }
            )

            # Add to knowledge base
            try:
                chunk_ids = await kb_manager.add_document(doc, kb_id)
                indexed_count += 1
                indexed_docs.append({
                    "doc_id": doc.id,
                    "title": doc.title,
                    "source": doc.source,
                    "chunks": len(chunk_ids),
                    "score": result.score
                })
            except Exception as e:
                print(f"[WebSearch] Failed to index {result.title}: {e}")

        return {
            "success": True,
            "search": search_result,
            "indexed": {
                "count": indexed_count,
                "documents": indexed_docs
            }
        }

    def quick_search(
        self,
        query: str,
        limit: int = 5
    ) -> List[WebSearchResult]:
        """
        Quick search with sensible defaults

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of search results
        """
        result = self.search(
            query=query,
            engine_type=self.ENGINE_GENERIC,
            time_range=self.TIME_ONE_MONTH,
            main_text=True,
            rerank_score=True,
            limit=limit
        )

        if result.get("success"):
            return result["results"]
        return []


class WebSearchScheduler:
    """
    Schedule periodic web searches and auto-indexing

    Features:
    - Scheduled searches (daily, weekly)
    - Topic-based monitoring
    - Deduplication
    - Auto-indexing to knowledge bases
    """

    def __init__(self):
        self.searcher = AliyunWebSearch()
        self.monitored_topics: Dict[str, Dict[str, Any]] = {}

    def add_topic(
        self,
        topic: str,
        kb_id: str = "default",
        schedule: str = "daily",  # daily, weekly
        engine_type: str = "GenericAdvanced",
        time_range: str = "OneDay"
    ):
        """Add a topic to monitor"""
        self.monitored_topics[topic] = {
            "kb_id": kb_id,
            "schedule": schedule,
            "engine_type": engine_type,
            "time_range": time_range,
            "last_run": None,
            "total_indexed": 0
        }

    def remove_topic(self, topic: str):
        """Remove a monitored topic"""
        self.monitored_topics.pop(topic, None)

    async def run_scheduled_searches(self):
        """Run all scheduled searches"""
        results = []

        for topic, config in self.monitored_topics.items():
            print(f"[WebSearchScheduler] Searching: {topic}")

            result = await self.searcher.search_and_index(
                query=topic,
                kb_id=config["kb_id"],
                engine_type=config["engine_type"],
                time_range=config["time_range"],
                auto_index=True
            )

            if result.get("success"):
                config["last_run"] = datetime.now().isoformat()
                config["total_indexed"] += result["indexed"]["count"]

            results.append({
                "topic": topic,
                "result": result
            })

        return results


# Singleton instances
_web_search: Optional[AliyunWebSearch] = None
_search_scheduler: Optional[WebSearchScheduler] = None


def get_web_search() -> AliyunWebSearch:
    """Get web search instance"""
    global _web_search
    if _web_search is None:
        _web_search = AliyunWebSearch()
    return _web_search


def get_search_scheduler() -> WebSearchScheduler:
    """Get search scheduler instance"""
    global _search_scheduler
    if _search_scheduler is None:
        _search_scheduler = WebSearchScheduler()
    return _search_scheduler
