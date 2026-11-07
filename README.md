# Portal Revival

Turn a discontinued Meta/Facebook Portal into a working photo frame with an AI coding agent, USB ADB, and the open-source [Frame app](https://github.com/Ishtiaqhossain/portal-frame).

This repository contains a portable **Agent Skill**, not a firmware image or a modified APK. It uses Meta's supported sideloading access and keeps the stock launcher. No root, bootloader unlock, or factory reset is part of the workflow.

## What it does

- Identifies the intended Portal, even with multiple Android devices attached.
- Records its original screensaver settings before changing them.
- Installs a verified Frame release and connects a Google Photos shared album, or sets up local phone uploads.
- Enables idle playback and optional side-by-side portrait photos.
- Checks the actual device and explains rollback and known limitations.

## Use with your agent

The portable package is [skills/revive-meta-portal](skills/revive-meta-portal/SKILL.md). Copy the **whole folder**, including its references and script, to your agent's skills directory. Do not overwrite an existing skill without reviewing it.

| Agent | Typical project installation | Invocation |
| --- | --- | --- |
| Codex | `.agents/skills/revive-meta-portal/` | `$revive-meta-portal` or a relevant natural-language request |
| Claude Code | `.claude/skills/revive-meta-portal/` | `/revive-meta-portal` or a relevant natural-language request |
| Other Agent Skills clients | The client's documented skills directory | Its skill loader or explicit skill invocation |
| A custom agent, including a LangGraph-based agent | Register the folder with the host's skill loader | Load `SKILL.md` and expose its referenced files and local execution tools |

For example, from this checkout on macOS/Linux:

```sh
mkdir -p /path/to/your/project/.agents/skills
cp -R skills/revive-meta-portal /path/to/your/project/.agents/skills/
```

For Claude Code, use `.claude/skills` instead. On Windows, copy the same folder using Explorer or PowerShell. Follow your client's discovery rules; the format does not guarantee automatic discovery in every framework. See the official [Agent Skills specification](https://agentskills.io/specification), [integration guide](https://agentskills.io/integrate-skills), [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills), and [Claude Code skill documentation](https://code.claude.com/docs/en/skills).

Example request:

> Use revive-meta-portal to turn my USB-connected Portal into a photo frame. Use my Google Photos shared album and show portrait photos side by side. Preserve the existing apps and photos, and verify idle playback.

## Requirements

- A Portal whose firmware exposes **Settings → Debug → ADB Enabled**.
- A USB data cable, a computer with [Android platform-tools](https://developer.android.com/tools/releases/platform-tools), and an authorized ADB connection.
- An agent that can read local files and run local commands. A cloud-only agent needs a trusted execution bridge to the computer holding the USB device; a skill cannot supply that connection.
- Internet access to download Frame and, for shared albums, on the Portal itself.
- Python 3.9+ for the optional snapshot helper. The helper uses only the standard library. No Meta CLI, RTK, Android SDK build tools, Google account password, or agent-specific API key is required for the normal setup.

Meta documents USB ADB for Portal, Portal Mini, Portal+, Portal Go, and Portal TV. **The workflow was exercised on a Portal and a Portal Mini running Android 10.** Other models and Windows/Linux agent execution have not been verified end to end. Mini grille removal is community-reported, model-dependent hardware guidance, not an official disassembly procedure.

## Read before setup

- Google Photos **shared albums** work; the private Favorites collection is not a shareable album. Add selected Favorites to a normal shared album. Anyone with its link can view the album.
- In Frame v1.2.0, album refresh runs on slideshow entry and about every 20 minutes while it is active. Ordinary additions/removals update after a successful refresh; an empty album or failed fetch can leave cached photos showing.
- Google/iCloud playback relies on unofficial provider web endpoints and can break when those providers change.
- Phone uploads use a token-bearing **HTTP** link on the home LAN. Keep the complete QR link, including `?k=…`; do not expose the upload port to the internet.
- In v1.2.0, upload requests are limited to 32 MiB. Stored phone uploads are capped at 300 photos or 500 MiB; older copies are evicted beyond those limits. Keep originals elsewhere.
- Portrait pairing combines consecutive portrait photos and crops each to its half. An unpaired portrait keeps the blurred side fill. This skill does not add blur detection or modify Google Photos.

The phone uploader was intermittently unreachable from a phone during the original setup even while Mac checks succeeded. That cause was not isolated; this repository does not claim to fix it. Reboot persistence has not been verified.

## Validate the helper

```sh
python3 -m unittest discover -s tests -v
```

The tests use simulated ADB responses and never access a device. An optional real-device snapshot is read-only on the Portal:

```sh
adb devices -l
python3 skills/revive-meta-portal/scripts/snapshot.py \
  --serial YOUR_DEVICE_SERIAL --output /private/path/before.json
```

Use a private existing output directory outside this repository. The helper refuses to overwrite a snapshot. It records settings and limited device/package metadata, not photos, account credentials, or Frame's upload token. It does **not** back up photo files or private app preferences. Its restrictive file mode is enforced on POSIX hosts; on Windows use a folder with appropriate access permissions.

## Publish your copy

After reviewing the files, create an empty repository on GitHub. From this local repository, add its actual remote URL and push:

```sh
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If a remote already exists, inspect it instead of replacing it blindly. Publishing this repository is separate from executing the skill on a device.

## Sharing and provenance

This is an independent community workflow, not a Meta or Frame release. Download the APK from the Frame maintainer's releases; no upstream binaries or source files are redistributed here. The initial hardware workflow used Frame **v1.2.0**. The skill tells agents to verify release metadata and APK compatibility rather than blindly installing whatever is newest.

Keep device snapshots, screenshots, album URLs, private upload links, signing keys, and downloaded APKs out of Git. Review the staged files before publishing. This repository's `.gitignore` is a convenience, not a privacy scanner.

The skill and original helper code are available under the [MIT license](LICENSE). Upstream apps retain their own licenses.
