from datetime import datetime, timezone
import unittest

from feeds.log_monitor import LogEntry, _is_noise_log_entry


class LogMonitorNoiseFiltersTest(unittest.TestCase):
    def _entry(self, message: str) -> LogEntry:
        return LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="ERROR",
            logger="sqlalchemy.pool.impl.AsyncAdaptedQueuePool",
            message=message,
            source="api",
            raw=message,
        )

    def test_connection_terminate_error_is_treated_as_noise(self) -> None:
        entry = self._entry(
            "Exception terminating connection <AdaptedConnection <asyncpg.connection.Connection object at 0x1234>>"
        )
        self.assertTrue(_is_noise_log_entry(entry))

    def test_cancel_scope_trace_line_is_treated_as_noise(self) -> None:
        entry = self._entry(
            "Cancelled via cancel scope 288889e9e50 by <Task pending name='Task-164'>"
        )
        self.assertTrue(_is_noise_log_entry(entry))


if __name__ == "__main__":
    unittest.main()
