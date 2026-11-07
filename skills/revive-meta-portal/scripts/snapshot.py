#!/usr/bin/env python3
"""Read a selected Android device's settings; create a private, new local snapshot."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


SETTINGS = (
    ("secure", "screensaver_components"),
    ("secure", "screensaver_enabled"),
    ("secure", "screensaver_activate_on_sleep"),
    ("secure", "screensaver_activate_on_dock"),
    ("system", "screen_off_timeout"),
)


def adb(*args):
    result = subprocess.run(
        ["adb", *args], check=True, capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip()


def collect(serial):
    devices = [line.split() for line in adb("devices", "-l").splitlines()]
    matches = [parts for parts in devices if len(parts) >= 2 and parts[0] == serial]
    if len(matches) != 1 or matches[0][1] != "device":
        raise ValueError("Selected serial must appear exactly once in state 'device'.")

    def shell(*args):
        return adb("-s", serial, "shell", *args)

    properties = {
        key: shell("getprop", key)
        for key in (
            "ro.product.model",
            "ro.product.device",
            "ro.build.version.release",
            "ro.build.version.sdk",
        )
    }
    settings = {}
    for namespace, key in SETTINGS:
        value = shell("settings", "get", namespace, key)
        settings[f"{namespace}/{key}"] = None if value == "null" else value

    installed = "package:com.portalhacks.frame" in shell(
        "pm", "list", "packages", "com.portalhacks.frame"
    ).splitlines()
    granted = None
    if installed:
        details = shell("dumpsys", "package", "com.portalhacks.frame")
        values = set(re.findall(
            r"android\.permission\.WRITE_SECURE_SETTINGS:\s+granted=(true|false)",
            details,
        ))
        if len(values) == 1:
            granted = values.pop() == "true"
    return {
        "format_version": 1,
        "serial": serial,
        "properties": properties,
        "settings": settings,
        "frame_installed": installed,
        "frame_write_secure_settings_granted": granted,
    }


def snapshot(serial, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError("Snapshot already exists; choose a new path.")
    data = collect(serial)
    payload = json.dumps(data, indent=2) + "\n"
    # Exclusive creation also rejects dangling symlinks and races with another writer.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(payload)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="Exact authorized ADB serial")
    parser.add_argument("--output", required=True, type=Path, help="New private JSON path")
    args = parser.parse_args()
    try:
        data = snapshot(args.serial, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Snapshot failed: {error}", file=sys.stderr)
        return 1
    print(f"Saved settings for {data['properties']['ro.product.model']} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
