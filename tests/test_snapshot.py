import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/revive-meta-portal/scripts/snapshot.py"
SPEC = importlib.util.spec_from_file_location("portal_snapshot", SCRIPT)
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def fake_adb(self, *args):
        if args == ("devices", "-l"):
            return "List of devices attached\ntest-mini device model:PortalMini\ntest-big device model:Portal"
        self.assertEqual(args[:3], ("-s", "test-mini", "shell"))
        command = args[3:]
        if command[:1] == ("getprop",):
            return "PortalMini" if command[1] == "ro.product.model" else "29"
        if command[:2] == ("settings", "get"):
            return "null" if command[3] == "screensaver_activate_on_dock" else "120000"
        if command[:3] == ("pm", "list", "packages"):
            return "package:com.portalhacks.frame\npackage:com.portalhacks.frame.other"
        if command[:2] == ("dumpsys", "package"):
            return "android.permission.WRITE_SECURE_SETTINGS: granted=true"
        self.fail(f"Unexpected ADB command: {args}")

    def test_targets_one_device_and_preserves_missing_settings(self):
        with patch.object(snapshot, "adb", side_effect=self.fake_adb):
            data = snapshot.collect("test-mini")
        self.assertEqual(data["serial"], "test-mini")
        self.assertTrue(data["frame_write_secure_settings_granted"])
        self.assertIsNone(data["settings"]["secure/screensaver_activate_on_dock"])
        self.assertEqual(data["settings"]["system/screen_off_timeout"], "120000")

    def test_absent_unauthorized_offline_and_ambiguous_serials_stop_before_shell(self):
        inventories = (
            "other device",
            "test-mini unauthorized",
            "test-mini offline",
            "test-mini device\ntest-mini device",
        )
        for inventory in inventories:
            with self.subTest(inventory=inventory):
                with patch.object(snapshot, "adb", return_value=inventory) as adb:
                    with self.assertRaises(ValueError):
                        snapshot.collect("test-mini")
                    adb.assert_called_once_with("devices", "-l")

    def test_unidentifiable_grant_remains_unknown(self):
        def responses(*args):
            if "dumpsys" in args:
                return "requested permissions: android.permission.WRITE_SECURE_SETTINGS"
            return self.fake_adb(*args)
        with patch.object(snapshot, "adb", side_effect=responses):
            self.assertIsNone(snapshot.collect("test-mini")["frame_write_secure_settings_granted"])

    def test_similarly_named_package_is_not_frame(self):
        def responses(*args):
            if "packages" in args:
                return "package:com.portalhacks.frame.other"
            return self.fake_adb(*args)
        with patch.object(snapshot, "adb", side_effect=responses):
            data = snapshot.collect("test-mini")
        self.assertFalse(data["frame_installed"])
        self.assertIsNone(data["frame_write_secure_settings_granted"])

    def test_snapshot_is_private_and_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "before.json"
            with patch.object(snapshot, "adb", side_effect=self.fake_adb):
                data = snapshot.snapshot("test-mini", output)
            self.assertEqual(json.loads(output.read_text()), data)
            if os.name == "posix":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with patch.object(snapshot, "adb") as adb:
                with self.assertRaises(FileExistsError):
                    snapshot.snapshot("test-mini", output)
                adb.assert_not_called()
            self.assertEqual(json.loads(output.read_text()), data)

    def test_failed_read_does_not_create_a_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "before.json"
            with patch.object(snapshot, "adb", side_effect=subprocess.TimeoutExpired("adb", 15)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    snapshot.snapshot("test-mini", output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
