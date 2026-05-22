import asyncio
import unittest
import sys
from unittest.mock import patch
from pathlib import Path
import importlib.util

from fastapi import HTTPException

# Add parent directory to path for direct imports
api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))


def load_system_module():
    system_path = api_dir / "routers" / "system.py"
    spec = importlib.util.spec_from_file_location("system_router", system_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


system_module = load_system_module()
check_docker_container = system_module.check_docker_container
restart_container = system_module.restart_container


class _Result:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class SystemRuntimeIdentityTest(unittest.TestCase):
    def test_check_docker_container_prefers_ike_alias_but_accepts_legacy(self):
        spec = {
            "key": "ike-postgres",
            "display_name": "IKE PostgreSQL",
            "aliases": ["ike-postgres", "myattention-postgres"],
        }

        side_effects = [
            _Result(1, ""),
            _Result(0, "running"),
            _Result(0, "running"),
            _Result(0, "healthy"),
        ]
        with patch.object(system_module.subprocess, "run", side_effect=side_effects):
            result = asyncio.run(check_docker_container(spec))

        self.assertEqual(result["name"], "IKE PostgreSQL")
        self.assertEqual(result["container_name"], "myattention-postgres")
        self.assertEqual(result["status"], "running")
        self.assertTrue(result["running"])

    def test_restart_container_accepts_legacy_alias_and_reports_resolution(self):
        side_effects = [
            _Result(1, ""),
            _Result(0, "running"),
            _Result(0, "myattention-postgres"),
        ]
        with patch.object(system_module.subprocess, "run", side_effect=side_effects):
            result = asyncio.run(restart_container("ike-postgres"))

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resolved_name"], "myattention-postgres")

    def test_restart_container_raises_for_unknown_name(self):
        with self.assertRaises(HTTPException):
            asyncio.run(restart_container("unknown-container"))
