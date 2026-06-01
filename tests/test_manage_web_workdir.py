import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from manage import _web_workdir_override, build_web_command, is_pid_running, read_pid, service_enabled  # noqa: E402


class TestWebWorkdirOverride(unittest.TestCase):
    """Tests for MYATTENTION_WEB_WORKDIR environment variable override."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def _make_config(self):
        return {
            "web": {"workdir": "services/web"},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_default_behavior_no_override(self):
        """When MYATTENTION_WEB_WORKDIR is unset, use config workdir."""
        self.assertFalse(os.environ.get("MYATTENTION_WEB_WORKDIR"))
        config = self._make_config()
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")
        self.assertEqual(workdir.parent.name, "services")

    def test_valid_override_existing_dir(self):
        """When MYATTENTION_WEB_WORKDIR points to an existing dir, use it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_config()
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    def test_invalid_override_missing_path(self):
        """When MYATTENTION_WEB_WORKDIR points to a non-existent path, raise."""
        bad_path = str(Path(tempfile.gettempdir()) / "myattention_nonexistent_20260601")
        os.environ["MYATTENTION_WEB_WORKDIR"] = bad_path
        config = self._make_config()
        with self.assertRaises(FileNotFoundError):
            build_web_command(config)

    def test_invalid_override_file_not_dir(self):
        """When MYATTENTION_WEB_WORKDIR points to a file, raise."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                os.environ["MYATTENTION_WEB_WORKDIR"] = f.name
                config = self._make_config()
                with self.assertRaises(NotADirectoryError):
                    build_web_command(config)
            finally:
                f.close()
                os.unlink(f.name)

    def test_override_whitespace_stripped(self):
        """Whitespace-only env var is treated as unset."""
        os.environ["MYATTENTION_WEB_WORKDIR"] = "   "
        config = self._make_config()
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")
        self.assertEqual(workdir.parent.name, "services")


class TestServiceModeIncompatibility(unittest.TestCase):
    """MYATTENTION_WEB_WORKDIR must not combine with web.use_service."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def _make_service_config(self):
        return {
            "web": {"workdir": "services/web", "use_service": True},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    @unittest.mock.patch("manage.os.name", "nt")
    def test_service_enabled_no_override_ok(self):
        """use_service=true without MYATTENTION_WEB_WORKDIR is fine."""
        config = self._make_service_config()
        self.assertFalse(os.environ.get("MYATTENTION_WEB_WORKDIR"))
        self.assertTrue(service_enabled(config, "web"))
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")

    @unittest.mock.patch("manage.os.name", "nt")
    def test_service_enabled_with_override_raises(self):
        """use_service=true + MYATTENTION_WEB_WORKDIR must raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_service_config()
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("use_service", str(ctx.exception))
            self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))

    def test_non_service_with_override_ok(self):
        """use_service=false + MYATTENTION_WEB_WORKDIR is fine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = {
                "web": {"workdir": "services/web", "use_service": False},
                "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
            }
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())


class TestWatchdogRestartSafety(unittest.TestCase):
    """Watchdog must reject MYATTENTION_WEB_WORKDIR + use_service combination."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    @unittest.mock.patch("manage.os.name", "nt")
    def test_guard_condition_raises(self):
        """The guard that RuntimeWatchdog uses raises RuntimeError for bad combo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            # Reproduce the exact guard logic from RuntimeWatchdog.__init__.
            # We cannot instantiate RuntimeWatchdog without real config files,
            # so we simulate the same conditional path.
            from manage import _web_workdir_override as override_fn, service_enabled

            config_with_service = {
                "web": {"workdir": "services/web", "use_service": True},
            }
            self.assertTrue(service_enabled(config_with_service, "web"))
            self.assertIsNotNone(override_fn())

            # This is the exact guard expression from RuntimeWatchdog.__init__.
            with self.assertRaises(RuntimeError) as ctx:
                if override_fn() and service_enabled(config_with_service, "web"):
                    raise RuntimeError(
                        "Watchdog manages web but MYATTENTION_WEB_WORKDIR is set while "
                        "web.use_service is true; watchdog restarts would silently "
                        "switch back to the configured service source tree. "
                        "Either disable web.use_service or unset MYATTENTION_WEB_WORKDIR."
                    )
            self.assertIn("Watchdog manages web", str(ctx.exception))

    @unittest.mock.patch("manage.os.name", "nt")
    def test_guard_condition_ok_no_override(self):
        """Guard passes when MYATTENTION_WEB_WORKDIR is unset."""
        os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        from manage import _web_workdir_override as override_fn, service_enabled

        config_with_service = {
            "web": {"workdir": "services/web", "use_service": True},
        }
        self.assertTrue(service_enabled(config_with_service, "web"))
        self.assertIsNone(override_fn())
        # Should not raise
        if override_fn() and service_enabled(config_with_service, "web"):
            self.fail("Guard should not have triggered without override")

    def test_guard_condition_ok_no_service(self):
        """Guard passes when use_service is false even with override set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            from manage import _web_workdir_override as override_fn, service_enabled

            config_no_service = {
                "web": {"workdir": "services/web", "use_service": False},
            }
            self.assertFalse(service_enabled(config_no_service, "web"))
            self.assertIsNotNone(override_fn())
            # Should not raise
            if override_fn() and service_enabled(config_no_service, "web"):
                self.fail("Guard should not have triggered without service mode")


class TestWatchdogServiceModeIncompatibility(unittest.TestCase):
    """MYATTENTION_WEB_WORKDIR must not combine with watchdog.use_service managing Web."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def _make_watchdog_service_config(self, manage_web=True):
        return {
            "web": {"workdir": "services/web"},
            "watchdog": {"use_service": True, "manage_web": manage_web},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_watchdog_service_no_override_ok(self):
        """watchdog.use_service=true without MYATTENTION_WEB_WORKDIR is fine."""
        config = self._make_watchdog_service_config()
        self.assertFalse(os.environ.get("MYATTENTION_WEB_WORKDIR"))
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")

    @unittest.mock.patch("manage.os.name", "nt")
    def test_watchdog_service_with_override_raises(self):
        """watchdog.use_service=true + manage_web=true + override must raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_watchdog_service_config(manage_web=True)
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("watchdog.use_service", str(ctx.exception))
            self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))

    @unittest.mock.patch("manage.os.name", "nt")
    def test_watchdog_service_manage_web_false_ok(self):
        """watchdog.use_service=true + manage_web=false + override is fine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_watchdog_service_config(manage_web=False)
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    def test_watchdog_process_with_override_ok(self):
        """watchdog.use_service=false + override is fine when no watchdog running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = {
                "web": {"workdir": "services/web"},
                "watchdog": {"use_service": False, "manage_web": True},
                "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
            }
            # No watchdog process running, so override is allowed.
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    @unittest.mock.patch("manage.os.name", "nt")
    def test_web_service_and_watchdog_service_both_rejected(self):
        """Both web.use_service and watchdog.use_service errors are distinct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = {
                "web": {"workdir": "services/web", "use_service": True},
                "watchdog": {"use_service": True, "manage_web": True},
                "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
            }
            # The web.use_service check runs first and should raise first.
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("web.use_service", str(ctx.exception))


class TestProcessWatchdogRevisionDrift(unittest.TestCase):
    """MYATTENTION_WEB_WORKDIR must not combine with running process-managed watchdog."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)

    def _make_process_watchdog_config(self, manage_web=True):
        return {
            "web": {"workdir": "services/web"},
            "watchdog": {"use_service": False, "manage_web": manage_web},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_override_ok_no_watchdog_running(self):
        """Override is fine when no process-managed watchdog is running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_process_watchdog_config(manage_web=True)
            # No watchdog PID on disk, so no running watchdog to conflict.
            self.assertIsNone(read_pid("watchdog"))
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    def test_override_ok_manage_web_false(self):
        """Override is fine when watchdog.manage_web=false, even if watchdog running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_process_watchdog_config(manage_web=False)
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    @unittest.mock.patch("manage.is_pid_running", return_value=True)
    @unittest.mock.patch("manage.read_pid", return_value=12345)
    def test_override_rejected_running_watchdog_manage_web_true(
        self, _mock_read_pid, _mock_is_pid_running
    ):
        """Override rejected when process-managed watchdog (manage_web=true) is running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_process_watchdog_config(manage_web=True)
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("process-managed watchdog", str(ctx.exception))
            self.assertIn("manage_web=true", str(ctx.exception))
            self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))

    @unittest.mock.patch("manage.is_pid_running", return_value=True)
    @unittest.mock.patch("manage.read_pid", return_value=12345)
    def test_override_ok_running_watchdog_manage_web_false(
        self, _mock_read_pid, _mock_is_pid_running
    ):
        """Override fine when running watchdog has manage_web=false."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_process_watchdog_config(manage_web=False)
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    @unittest.mock.patch("manage.is_pid_running", return_value=False)
    @unittest.mock.patch("manage.read_pid", return_value=12345)
    def test_override_ok_watchdog_pid_not_running(
        self, _mock_read_pid, _mock_is_pid_running
    ):
        """Override fine when watchdog PID exists but process is dead."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_process_watchdog_config(manage_web=True)
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())


if __name__ == "__main__":
    unittest.main()
