import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from manage import build_web_command  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
