import asyncio
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from db.session import async_session_maker, engine

RUNTIME_TABLES = [
    "runtime_outbox_events",
    "runtime_task_checkpoints",
    "runtime_memory_packets",
    "runtime_work_contexts",
    "runtime_worker_leases",
    "runtime_task_events",
    "runtime_decisions",
    "runtime_tasks",
    "runtime_projects",
]


class SyncAsyncSessionAdapter:
    """Expose a small sync-style surface for legacy DB-backed pytest suites."""

    def __init__(self, runner: asyncio.Runner, session):
        self._runner = runner
        self._session = session

    def execute(self, statement, params=None):
        if isinstance(statement, str):
            statement = text(statement)
        return self._runner.run(self._session.execute(statement, params or {}))

    def commit(self):
        return self._runner.run(self._session.commit())

    def rollback(self):
        return self._runner.run(self._session.rollback())

    def flush(self):
        return self._runner.run(self._session.flush())

    def add(self, instance):
        self._session.add(instance)

    def add_all(self, instances):
        self._session.add_all(instances)

    def delete(self, instance):
        return self._runner.run(self._session.delete(instance))


@pytest.fixture(scope="session")
def async_runner():
    """Keep one event loop alive across DB-backed tests to avoid pooled-loop drift."""
    with asyncio.Runner() as runner:
        yield runner
        runner.run(engine.dispose())


@pytest.fixture
def db_session(async_runner):
    """Runtime DB-backed tests use the project async session through a sync adapter."""
    session = async_session_maker()
    adapter = SyncAsyncSessionAdapter(async_runner, session)
    # Fail fast on unavailable DB so test output reflects the real blocker.
    adapter.execute("SELECT 1")
    try:
        yield adapter
    finally:
        try:
            adapter.rollback()
        finally:
            async_runner.run(session.close())


@pytest.fixture(autouse=True)
def clean_runtime_tables(request):
    """Keep runtime DB-backed tests isolated across function/class boundaries."""
    runtime_db_backed_files = {
        "test_runtime_v0_schema_foundation.py",
        "test_runtime_v0_postgres_claim_verifier.py",
        "test_runtime_v0_operational_closure.py",
        "test_runtime_v0_project_surface.py",
        "test_runtime_v0_benchmark_bridge.py",
        "test_runtime_v0_controller_acceptance.py",
    }
    if request.fspath.basename not in runtime_db_backed_files:
        return
    db_session = request.getfixturevalue("db_session")
    for table in RUNTIME_TABLES:
        db_session.execute(f"DELETE FROM {table}")
    db_session.commit()
