---
name: revive-meta-portal
description: Repurpose an owner-authorized Meta or Facebook Portal as a photo frame using USB ADB and the open-source Frame app. Use for deprecated Portal setup, Google Photos shared albums, local photo uploads, side-by-side portraits, screensaver troubleshooting, and reverting this setup. Not for PlayStation Portal or account recovery.
license: MIT
---

# Revive a Meta Portal

Restore useful photo playback through sideloading. Preserve the user's existing apps, photos, account setup, and launcher. This skill needs a local execution tool with access to the USB-connected device; standard skill support alone does not provide hardware access.

## Establish the target and requested outcome

1. Inspect `adb devices -l`. Use the explicitly selected **serial on every device command**. If multiple devices are plausible, resolve the intended one before mutation. An `unauthorized` or `offline` target is not ready.
2. Read its model, Android/API version, display size, and available storage. Check whether Frame is already installed and configured; avoid reinstalling a working setup for a settings change.
3. Identify the desired source: a user-provided Google Photos shared album, supported iCloud shared album, or local phone uploads. Do not request Google credentials or change/delete cloud photos. Private Google Photos Favorites cannot be linked directly.
4. Save original screensaver values before the first change. The optional [snapshot helper](scripts/snapshot.py) makes a serial-specific, read-only snapshot:

   ```sh
   python3 scripts/snapshot.py --serial YOUR_DEVICE_SERIAL --output /private/path/before.json
   ```

   Resolve that script relative to this skill folder; choose an existing private output directory outside the public checkout. The helper does not back up app data, uploaded photos, or Frame's guard/pairing preferences. For an existing installation, record any options/services you intend to change separately, without exposing its upload token.

## Execute the applicable workflow

Read [setup.md](references/setup.md) for APK provenance, installation, album configuration, screensaver selection, portrait pairing, verification, and rollback. Read [troubleshooting.md](references/troubleshooting.md) only for the relevant failure or hidden-port question.

- Prefer a maintainer-published Frame APK over building the Meta sample or a custom app for this photo-frame task. The package verified in the original setup was `com.portalhacks.frame`, release v1.2.0. Check current source/release details before assuming those interfaces remain unchanged.
- Select a trusted release compatible with the observed API level. Compare its SHA-256 against release metadata or the maintainer's checksum and verify the APK signature when tooling is available. A valid signature does not establish that a binary was built from the inspected source.
- Installing Frame and setting it as the screensaver are within a request to perform this setup. Preserve already-granted permissions and unrelated settings. Use the user's preference for pairing; do not silently crop single photos or change the idle timeout permanently.
- Keep the stock launcher and Meta settings accessible. Do not factory-reset, root, unlock/flash the bootloader, clear app data, uninstall system packages, or change display density as a shortcut. A package signature conflict is a reason to stop that update and preserve data, not to uninstall the existing app.
- A custom build cannot normally replace the published APK without the original signing key. If a requested feature requires a separate package, explain its separate private storage and migration limits before switching the active setup.

## Verify and report

Verify the requested setting or the real photos on the actual device, plus automatic idle playback when changing the screensaver. Restore any temporary test timeout even if verification fails. Do not report a screenshot taken during loading or a sample image as proof that the user's album loaded.

For phone upload connectivity, test the complete authenticated HTTP URL and the bare URL separately. A bare-link 403 is expected authentication behavior. A successful Mac test does not prove a failing phone can connect. Get the phone's exact error and point of failure rather than diagnosing from a generic "not loading."

Prefer read-only checks and the user's existing album over test uploads. Never delete by a stale thumbnail position: another person's upload can arrive between inspection and a cleanup tap. Only remove an explicitly identified test artifact you created; leave other photos alone.

Report what changed, what was observed, the rollback location, and what remains unverified. Keep serials, screenshots, album links, and token-bearing upload URLs in private local evidence, not this skill or a public repository.

## Explain the actual limits

For the tested v1.2.0 source:

- Shared albums refresh when the slideshow enters the foreground and about every 20 minutes while active. Additions/removals need a successful network refresh. Empty albums and failed fetches can retain an old cache; do not promise immediate or complete erasure.
- Google/iCloud shared-album fetching uses unofficial web endpoints. The entire private photo library and Favorites are not accessible through this workflow. A share link exposes that album to anyone holding it.
- Phone uploads stay in private app storage, use a per-install token, and travel over HTTP on the LAN. Requests are capped at 32 MiB; stored uploads at 300 photos or 500 MiB, evicting older copies beyond those limits. Uninstalling or clearing Frame data loses these copies.
- Pairing combines consecutive portrait photos, crops each to its half, and leaves unpaired portraits with blurred sides. It does not detect or skip out-of-focus originals.
- Reboot persistence and phone-browser reliability must be verified independently. USB ADB may need re-enabling after a reboot. Do not advertise wireless-only first-time setup or automatic support for every Portal model.

## Sources

- [Meta Portal setup](https://developers.meta.com/vr/documentation/android-apps/portal-setup/)
- [Meta Portal samples](https://github.com/meta-quest/portal-samples)
- [Frame releases and documentation](https://github.com/Ishtiaqhossain/portal-frame)

Model-specific community evidence and source paths for version-dependent behavior are linked in the references.
