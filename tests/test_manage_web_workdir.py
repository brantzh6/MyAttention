import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from manage import _web_workdir_override, build_web_command, service_enabled  # noqa: E402


def mock_service_enabled(name: str, enabled: bool):
    """Return a patcher that mocks service_enabled for a specific component."""
    original_fn = service_enabled

    def mock_fn(config, component):
        if component == name:
            return enabled
        return original_fn(config, component)

    return unittest.mock.patch("manage.service_enabled", side_effect=mock_fn)


class TestWebWorkdirOverride(unittest.TestCase):
    """Tests for MYATTENTION_WEB_WORKDIR environment variable override."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        self.original_ops_state = os.environ.pop("IKE_OPS_STATE_PATH", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        if self.original_ops_state is not None:
            os.environ["IKE_OPS_STATE_PATH"] = self.original_ops_state
        else:
            os.environ.pop("IKE_OPS_STATE_PATH", None)

    def _make_ops_state_file(self, tmpdir: str) -> Path:
        ops_state_file = Path(tmpdir) / "ops_state.json"
        ops_state_file.write_text("{}", encoding="utf-8")
        return ops_state_file

    def _make_config(self):
        return {
            "web": {"workdir": "services/web"},
            "watchdog": {"manage_web": False},
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
            ops_state_file = self._make_ops_state_file(tmpdir)
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(ops_state_file)
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
        self.original_ops_state = os.environ.pop("IKE_OPS_STATE_PATH", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        if self.original_ops_state is not None:
            os.environ["IKE_OPS_STATE_PATH"] = self.original_ops_state
        else:
            os.environ.pop("IKE_OPS_STATE_PATH", None)

    def _make_ops_state_file(self, tmpdir: str) -> Path:
        ops_state_file = Path(tmpdir) / "ops_state.json"
        ops_state_file.write_text("{}", encoding="utf-8")
        return ops_state_file

    def _make_config(self, use_service=False):
        return {
            "web": {"workdir": "services/web", "use_service": use_service},
            "watchdog": {"manage_web": False},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_service_disabled_with_override_ok(self):
        """use_service=false + MYATTENTION_WEB_WORKDIR is fine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ops_state_file = self._make_ops_state_file(tmpdir)
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(ops_state_file)
            with mock_service_enabled("web", False):
                config = self._make_config(use_service=False)
                _cmd, workdir, _env = build_web_command(config)
                self.assertEqual(workdir, Path(tmpdir).resolve())

    def test_service_enabled_with_override_raises(self):
        """use_service=true + MYATTENTION_WEB_WORKDIR must raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            with mock_service_enabled("web", True):
                config = self._make_config(use_service=True)
                with self.assertRaises(RuntimeError) as ctx:
                    build_web_command(config)
                self.assertIn("web.use_service", str(ctx.exception))
                self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))


class TestWatchdogManageWebBoundary(unittest.TestCase):
    """MYATTENTION_WEB_WORKDIR requires watchdog.manage_web=false."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        self.original_ops_state = os.environ.pop("IKE_OPS_STATE_PATH", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        if self.original_ops_state is not None:
            os.environ["IKE_OPS_STATE_PATH"] = self.original_ops_state
        else:
            os.environ.pop("IKE_OPS_STATE_PATH", None)

    def _make_ops_state_file(self, tmpdir: str) -> Path:
        ops_state_file = Path(tmpdir) / "ops_state.json"
        ops_state_file.write_text("{}", encoding="utf-8")
        return ops_state_file

    def _make_config(self, manage_web=True):
        return {
            "web": {"workdir": "services/web"},
            "watchdog": {"manage_web": manage_web},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_no_override_manage_web_true_ok(self):
        """manage_web=true without override is fine."""
        config = self._make_config(manage_web=True)
        self.assertIsNone(_web_workdir_override())
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")

    def test_override_manage_web_false_ok(self):
        """manage_web=false + override is supported."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ops_state_file = self._make_ops_state_file(tmpdir)
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(ops_state_file)
            config = self._make_config(manage_web=False)
            _cmd, workdir, _env = build_web_command(config)
            self.assertEqual(workdir, Path(tmpdir).resolve())

    def test_override_manage_web_true_raises(self):
        """manage_web=true + override must raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = self._make_config(manage_web=True)
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("watchdog.manage_web=false", str(ctx.exception))
            self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))

    def test_override_manage_web_omitted_raises(self):
        """manage_web omitted (default true) + override must raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            config = {
                "web": {"workdir": "services/web"},
                "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
            }
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("watchdog.manage_web=false", str(ctx.exception))

    def test_no_override_manage_web_false_ok(self):
        """manage_web=false without override is fine."""
        config = self._make_config(manage_web=False)
        self.assertIsNone(_web_workdir_override())
        _cmd, workdir, _env = build_web_command(config)
        self.assertEqual(workdir.name, "web")

    def test_service_enabled_and_manage_web_true_both_checked(self):
        """Both web.use_service and manage_web=true are checked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            with mock_service_enabled("web", True):
                config = {
                    "web": {"workdir": "services/web", "use_service": True},
                    "watchdog": {"manage_web": True},
                    "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
                }
                # web.use_service check runs first.
                with self.assertRaises(RuntimeError) as ctx:
                    build_web_command(config)
                self.assertIn("web.use_service", str(ctx.exception))


class TestOpsStatePathInjection(unittest.TestCase):
    """MYATTENTION_WEB_WORKDIR requires IKE_OPS_STATE_PATH for durable contract."""

    def setUp(self):
        self.original_workdir = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        self.original_ops_state = os.environ.pop("IKE_OPS_STATE_PATH", None)

    def tearDown(self):
        if self.original_workdir is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original_workdir
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        if self.original_ops_state is not None:
            os.environ["IKE_OPS_STATE_PATH"] = self.original_ops_state
        else:
            os.environ.pop("IKE_OPS_STATE_PATH", None)

    def _make_config(self):
        return {
            "web": {"workdir": "services/web"},
            "watchdog": {"manage_web": False},
            "runtime": {"api_port": 8000, "web_port": 3000, "web_host": "127.0.0.1"},
        }

    def test_override_with_valid_ops_state_path_injects_env(self):
        """When override is set with valid IKE_OPS_STATE_PATH, env includes it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ops_state_file = Path(tmpdir) / "ops_state.json"
            ops_state_file.write_text("{}", encoding="utf-8")
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(ops_state_file)
            config = self._make_config()
            _cmd, _workdir, env = build_web_command(config)
            self.assertEqual(env["IKE_OPS_STATE_PATH"], str(ops_state_file.resolve()))

    def test_override_missing_ops_state_path_raises(self):
        """When override is set without IKE_OPS_STATE_PATH, raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ.pop("IKE_OPS_STATE_PATH", None)
            config = self._make_config()
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("IKE_OPS_STATE_PATH", str(ctx.exception))
            self.assertIn("MYATTENTION_WEB_WORKDIR", str(ctx.exception))

    def test_override_whitespace_ops_state_path_raises(self):
        """Whitespace-only IKE_OPS_STATE_PATH is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = "   "
            config = self._make_config()
            with self.assertRaises(RuntimeError) as ctx:
                build_web_command(config)
            self.assertIn("IKE_OPS_STATE_PATH", str(ctx.exception))

    def test_override_nonexistent_ops_state_path_raises(self):
        """IKE_OPS_STATE_PATH pointing to non-existent file raises."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent = Path(tmpdir) / "nonexistent_ops_state.json"
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(nonexistent)
            config = self._make_config()
            with self.assertRaises(FileNotFoundError) as ctx:
                build_web_command(config)
            self.assertIn("IKE_OPS_STATE_PATH", str(ctx.exception))

    def test_no_override_no_ops_state_required(self):
        """When override is unset, IKE_OPS_STATE_PATH is not required."""
        os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        os.environ.pop("IKE_OPS_STATE_PATH", None)
        config = self._make_config()
        _cmd, _workdir, env = build_web_command(config)
        self.assertNotIn("IKE_OPS_STATE_PATH", env)


class TestRuntimeWatchdogBoundary(unittest.TestCase):
    """RuntimeWatchdog must reject override when manage_web=true."""

    def setUp(self):
        self.original = os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        self.original_ops_state = os.environ.pop("IKE_OPS_STATE_PATH", None)

    def tearDown(self):
        if self.original is not None:
            os.environ["MYATTENTION_WEB_WORKDIR"] = self.original
        else:
            os.environ.pop("MYATTENTION_WEB_WORKDIR", None)
        if self.original_ops_state is not None:
            os.environ["IKE_OPS_STATE_PATH"] = self.original_ops_state
        else:
            os.environ.pop("IKE_OPS_STATE_PATH", None)

    def _make_ops_state_file(self, tmpdir: str) -> Path:
        ops_state_file = Path(tmpdir) / "ops_state.json"
        ops_state_file.write_text("{}", encoding="utf-8")
        return ops_state_file

    def test_watchdog_init_manage_web_true_with_override_raises(self):
        """RuntimeWatchdog rejects override when manage_web=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            from runtime_watchdog import RuntimeWatchdog

            # Create minimal config file for load_runtime_config.
            config_dir = REPO_ROOT / "config" / "runtime"
            config_dir.mkdir(parents=True, exist_ok=True)
            test_config_path = config_dir / "test-boundary.toml"
            test_config_path.write_text(
                """
[web]
workdir = "services/web"

[watchdog]
manage_web = true

[runtime]
api_port = 8000
web_port = 3000
""",
                encoding="utf-8",
            )

            try:
                with self.assertRaises(RuntimeError) as ctx:
                    RuntimeWatchdog("test-boundary")
                self.assertIn("watchdog.manage_web=false", str(ctx.exception))
            finally:
                test_config_path.unlink()

    def test_watchdog_init_manage_web_false_with_override_ok(self):
        """RuntimeWatchdog accepts override when manage_web=false."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ops_state_file = self._make_ops_state_file(tmpdir)
            os.environ["MYATTENTION_WEB_WORKDIR"] = tmpdir
            os.environ["IKE_OPS_STATE_PATH"] = str(ops_state_file)
            from runtime_watchdog import RuntimeWatchdog

            config_dir = REPO_ROOT / "config" / "runtime"
            config_dir.mkdir(parents=True, exist_ok=True)
            test_config_path = config_dir / "test-boundary-ok.toml"
            test_config_path.write_text(
                """
[web]
workdir = "services/web"

[watchdog]
manage_web = false

[runtime]
api_port = 8000
web_port = 3000
""",
                encoding="utf-8",
            )

            try:
                watchdog = RuntimeWatchdog("test-boundary-ok")
                self.assertFalse(watchdog.manage_web)
            finally:
                test_config_path.unlink()


if __name__ == "__main__":
    unittest.main()