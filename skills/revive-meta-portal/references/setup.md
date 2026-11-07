# Setup, verification, and rollback

Commands below use POSIX shell syntax. On Windows use equivalent PowerShell quoting or Python argument vectors; keep the explicit serial and correctly quote arguments forwarded to Android's shell. Replace examples with observed inputs. Do not copy another user's serial, IP, token, or share link.

## Inspect and snapshot

Enable **Settings → Debug → ADB Enabled**, attach a USB data cable, and accept the computer's debugging prompt. Follow [Meta's guide](https://developers.meta.com/vr/documentation/android-apps/portal-setup/). An ADB toggle does not itself establish a wireless connection.

```sh
adb devices -l
SERIAL='YOUR_DEVICE_SERIAL'
adb -s "$SERIAL" shell getprop ro.product.model
adb -s "$SERIAL" shell getprop ro.build.version.sdk
adb -s "$SERIAL" shell wm size
adb -s "$SERIAL" shell df -h /sdcard
adb -s "$SERIAL" shell pm path com.portalhacks.frame
```

Run `scripts/snapshot.py` from the skill folder before changing secure settings. It records the target serial, model/API, five screensaver/timeout values, whether Frame is installed, and its secure-settings permission when identifiable. Never replace the first snapshot with a post-change snapshot. For an existing Frame installation, record the relevant UI switches and guard-service state as well; those private preferences are not in the snapshot.

Portal runs an older Android variant without Google Mobile Services. The Frame v1.2.0 APK used here has minimum API 28 and targets API 29. Confirm compatibility for the actual APK and device; the hardware family name alone is insufficient.

## Obtain and verify Frame

Use the maintainer's [release page](https://github.com/Ishtiaqhossain/portal-frame/releases), not an APK mirror. Save the release tag, download URL, expected hash, actual hash, and signer details in private evidence. As a known tested baseline:

| Item | Frame v1.2.0 |
| --- | --- |
| Package | `com.portalhacks.frame` |
| Asset | `Frame-v1.2.0.apk` |
| APK SHA-256 | `2d1a2cba770ae887bb5032929bbd4d2c1897cde2f05b30fd4bac77a50f385af9` |
| Signer certificate SHA-256 | `920904740569f9a26c4fb1d6c285a44d50138e6a1f3d85e69ed8a17beb11469d` |

These fingerprints describe that historical release; they are not expected to match a future release. For another release, obtain its published digest/checksum and inspect its compatibility and interfaces. Hash matching is an integrity check against the selected publisher, not an independent security audit.

Use Python's `hashlib.sha256`, `sha256sum`, or `shasum -a 256`. If Android build tools are available:

```sh
aapt dump badging /private/path/Frame.apk
apksigner verify --verbose --print-certs /private/path/Frame.apk
```

If signer inspection tooling is unavailable, report that limitation; do not claim verification. Do not install an entire build environment merely to sideload an already verified APK unless needed or requested.

```sh
adb -s "$SERIAL" install /private/path/Frame.apk
adb -s "$SERIAL" shell am start -n com.portalhacks.frame/.SettingsActivity
```

For an explicitly intended update, `install -r` preserves app data when signatures are compatible. Do not resolve `INSTALL_FAILED_UPDATE_INCOMPATIBLE` by uninstalling: phone uploads and preferences can be lost.

## Connect photos

**Google Photos:** ask for a shared **album** link. On the Portal choose **Frame → Add album**, scan an album QR or paste its link. A QR is only a representation of the exact URL; generate it locally with an installed QR encoder and verify by decoding when possible. Do not send a private link to a public QR-generation website.

Google Photos Favorites is a special collection. The user can select its photos and use **Add to album** to put them into a normal shared album. New favorites do not automatically join that album. Do not modify the user's Google Photos collection on their behalf as part of Portal setup.

**iCloud:** use a shared album whose **Public Website** is enabled, if that is the user's choice. Both providers' link holders can view the shared album; avoid suggesting the user's entire library be made public.

The v1.2.0 exported receiver also supports adding an album over ADB. Validate the recognized HTTPS share URL and quote it for Android's remote shell, not just the host shell. A portable Python example, with `serial` and `album_url` set from the user's selected inputs:

```python
import shlex
import subprocess

command = (
    "am broadcast -n com.portalhacks.frame/.ConfigReceiver --es url "
    + shlex.quote(album_url)
)
subprocess.run(["adb", "-s", serial, "shell", command], check=True)
```

A nonempty supported URL adds an album idempotently; an **empty `url` extra clears all albums**. Never send it as a placeholder or to test the receiver. A broadcast's zero result alone is not proof that the album fetched successfully: inspect the UI and sanitized device logs, and confirm actual album photos appear.

**Local phone uploads:** open **Add photos from a phone** and scan the QR with a phone on the same LAN. The correct link resembles `http://DEVICE_IP:PORT/?k=TOKEN`. The port is often 8080 but can differ. Discover it on the device rather than guessing. The album QR and the phone-upload QR serve different purposes.

## Screensaver and optional portraits

To keep Frame selected when the stock launcher reclaims the screensaver, grant the declared permission and enable the guard. This grant allows the app to write secure settings; explain its purpose and record whether it was already granted.

```sh
adb -s "$SERIAL" shell pm grant com.portalhacks.frame android.permission.WRITE_SECURE_SETTINGS
adb -s "$SERIAL" shell am start -n com.portalhacks.frame/.SettingsActivity
adb -s "$SERIAL" shell am broadcast -n com.portalhacks.frame/.ConfigReceiver --ez guard true
```

The UI's **Use as screensaver** button also enables the guard when the permission exists. Do not run two competing screensaver guards. If another launcher manages the screensaver, inspect and resolve that specific conflict rather than removing the launcher.

If the user wants side-by-side portraits:

```sh
adb -s "$SERIAL" shell am broadcast -n com.portalhacks.frame/.ConfigReceiver --ez pairs true
adb -s "$SERIAL" shell am start -f 0x10008000 -n com.portalhacks.frame/.SlideshowComposeActivity
```

The flags create a fresh slideshow task so construction-time settings take effect; they do not clear app data. Verify **Frame → Customize → Playback → Pair photos to fill the screen** is ON. Leave **Zoom single photos to fill** as the user chose it; it is a separate crop setting. Reopen the slideshow after a UI check. Pairing may crop each picture to its half, so do not promise that every pixel of each original remains visible.

## Verify on the device

- Confirm the expected album loads and real photos render. A photo count in logs supports fetching, not proof of every image rendering. Keep URLs, album names, and upload tokens out of public logs.
- Check `settings get secure screensaver_components`: for this release it should be `com.portalhacks.frame/.FrameDreamService` when selected. Check the relevant switches in the UI; a receiver result alone is insufficient.
- Return home and verify that idle playback starts by itself. Prefer the normal timeout. If briefly shortening `screen_off_timeout`, save its original value first and restore it in a `finally` block even on timeout, exception, or assertion failure. Do not claim an idle test passed if user interaction interrupted it; retry only that check.
- The dream service hands off to `SlideshowComposeActivity` and finishes. `dumpsys dreams` showing no active dream can therefore be normal. Check the resumed activity and the handoff log as well as the visible display.
- Check for recent Frame crashes. Do not reboot just to test persistence unless that interruption is within the requested work; report untested reboot behavior.
- Repeat configuration separately for each selected device. No command without `-s` should accidentally configure the other connected Portal.

## Revert only the changes made

Use the **matching serial's** snapshot and any recorded pre-existing Frame UI/service state. Before restoring system settings, disable Frame's guard so it does not immediately reclaim them:

```sh
adb -s "$SERIAL" shell am broadcast -n com.portalhacks.frame/.ConfigReceiver --ez guard false
```

For each setting changed by this setup, restore the saved namespace/key/value with `settings put`; if the saved JSON value is null, remove the introduced setting with `settings delete`. For example, if `secure/screensaver_enabled` was originally null, restore absence with `adb -s "$SERIAL" shell settings delete secure screensaver_enabled`. Quote component strings when forwarding to the remote shell. Do not substitute a hardcoded stock component for an observed value, and do not revert unrelated later changes.

Revoke `WRITE_SECURE_SETTINGS` only if this setup newly granted it; preserve a pre-existing grant. If returning to an earlier Frame configuration, restore the previous guard/pairing switches and active component. Explain any unknown private-preference state instead of inventing a backup. Keeping the installed app preserves its phone uploads. Uninstalling or clearing it is not required for rollback.

## Version-dependent source facts

Inspected Frame source commit: `4affee8c57c2b47488ff53755094a4d6e32ad74e`; device-tested published APK: v1.2.0. The source checkout and published binary were not reproducibly compared.

- `ConfigReceiver.kt`: `url`, `guard`, `pairs`, `zoom_fill` broadcast inputs.
- `SlideshowComposeActivity.kt`: 20-minute refresh; only nonempty fetches replace album caches.
- `SlideshowController.kt`: consecutive portrait pairing.
- `LocalDropServer.kt`: full token URL, preferred ports, 32 MiB request limit.
- `LocalUploads.kt`: 300-file / 500 MiB retention cap.

Recheck these interfaces for a different release. See [Frame's repository](https://github.com/Ishtiaqhossain/portal-frame) and [Google's album instructions](https://support.google.com/photos/answer/6128849).
