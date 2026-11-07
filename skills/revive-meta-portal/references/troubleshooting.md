# Troubleshooting and hardware access

## No obvious USB port

First establish the exact model from its label or settings. Meta documents USB-C ADB across the Portal family; the connector's physical access varies. A small display is not enough to identify the enclosure.

- **Portal Mini DT90GB:** a firsthand hardware report shows the data port behind the rear speaker grille. Some owners report a counterclockwise twist when facing the grille; others needed a shallow plastic opening pick around its perimeter on the first removal. Unplug power first, support the screen on a soft surface, leave the rubber Portal logo attached, and stop if the cover bends or requires excessive force. Do not apply generic knife/prying advice to an unidentified model.
- **Portal Go:** Meta documents the USB-C port beneath a rubber cover. Do not substitute the Mini's grille procedure.
- Other revisions can have a different cover. Ask for the model or a rear photo before giving disassembly instructions where the access point remains unclear.

Sources: [Meta setup](https://developers.meta.com/vr/documentation/android-apps/portal-setup/), [firsthand Mini DT90GB port photo/report](https://www.cmos486.es/blog/portal-mini-wallpanel-home-assistant), [Mini owner removal experiences](https://www.reddit.com/r/FacebookPortal/comments/1u6lmvx/has_anyone_successfully_accessed_the_usb_port/). Community evidence is not an official service procedure and does not guarantee identical retaining tabs on another unit.

## ADB missing, unauthorized, or offline

- `adb` missing: obtain Android platform-tools for the host OS. A full Android Studio installation is unnecessary for normal sideloading.
- No device: use a data-capable cable, the actual USB-C data port, normal device power, and a direct USB connection. Check ADB is still enabled. A phone's charging cable may not carry data.
- `unauthorized`: unlock the Portal and accept its debugging trust prompt.
- `offline`: check cable and device state; re-enumerate before continuing. Avoid restarting a shared ADB server when other device work is running.
- ADB may need re-enabling after reboot. Do not factory-reset a configured Portal to recover a missing menu without investigating existing firmware/account state and the risk to photos/setup.

Wireless ADB on older Android typically needs an authorized USB session first, followed by `adb -s SERIAL tcpip 5555` and `adb connect DEVICE_IP:5555` on a trusted LAN. It is optional, is not enabled by merely toggling USB ADB, may not survive reboot, and should not be exposed to the internet. Do not assume Android 11+ pairing-code instructions apply to Android 10 Portal firmware. See [Android ADB documentation](https://developer.android.com/tools/adb#wireless).

## Phone upload page does not load

Establish which step failed: opening the page, choosing photos, or posting them. Get the phone/browser and exact visible error before claiming a cause.

1. Check the Portal's current Wi-Fi IP and the link displayed in Frame. DHCP can change the IP; the port can also change if a preferred port is busy.
2. Use the **full** `http://…/?k=…` link. The bare IP/port intentionally responds 403. Keep HTTP; the local server does not provide HTTPS.
3. Test from the agent's computer without publishing the token: bare URL should reject access, complete link should return the upload form. Do not print the token-bearing URL in shared logs.
4. If it works on the computer but not the phone, check the phone is on the same home LAN, not guest Wi-Fi or cellular, and temporarily test without a VPN. Do not infer the exact cause from those checks alone.
5. Check Frame's process, `DropServerService`, and sanitized `PortalFrame`/`AndroidRuntime` logs. A running service is not proof its socket responds. Avoid resetting data or interrupting an active upload as a diagnostic shortcut.
6. If posting fails, try a small batch below the tested v1.2.0 limit of 32 MiB per request. Account for HEIC conversion/file selection time on the phone. A network-page failure and a rejected oversized upload are different failures.

The token is stable for an installation in the inspected source; it is not a single-use QR. It can change after clearing/reinstalling app data. Do not promise a saved link remains valid across IP, port, or installation changes.

## Album is missing or stale

Confirm it is a public-by-link shared album, not a private library URL or Favorites collection. Preserve the user's sharing choices; don't publish the whole library to make one album work.

The v1.2.0 app refreshes on slideshow entry and every 20 minutes while active. Open the slideshow again to request a fresh fetch; a successful fetch still takes network time. Empty results or network/provider failures leave older cached photos. Removing one photo from a nonempty album normally updates on the next successful refresh; emptying the album does not reliably clear the display. Phone-uploaded copies are a separate source and are not removed by editing a cloud album.

Google/iCloud parsing can break when provider pages change. Record observed HTTP/fetch errors, installed app version, and sanitized evidence; distinguish an upstream change from Wi-Fi failure. Do not claim every album photo loaded because a sample photo displayed.

## Screensaver or portrait setting seems ignored

- Verify the installed release's receiver/activity names before sending commands.
- Check the UI setting and recreate the slideshow task after a pairing change. Settings read at construction do not necessarily update an existing task.
- The launcher can reclaim the dream selection. Check the declared secure-settings grant and Frame's opted-in guard. Preserve the original selection and grant state for rollback.
- Other launchers can also own the screensaver slot. Resolve a confirmed conflict without running competing guards.
- Paired portraits must be consecutive; the next landscape photo does not form a pair. Single-photo blur fill is separate from **Ambient color glow**. Turning the glow off does not remove the composited blurred side fill.
- A sharp subject with an intentionally blurred portrait-mode background is not an out-of-focus photo. Stock v1.2.0 has no blur-skipping filter; do not claim pairing provides one or silently modify the user's cloud album.
