# DualSense Drift Lab

Measure stick drift on a Sony DualSense / DualSense Edge, back up the controller's
calibration, and optionally recentre the sticks — all from the browser, via WebHID.

No install. No drivers. No account. Nothing leaves your machine.

![single-file html](https://img.shields.io/badge/file-single%20HTML-1f6feb)

## Why this exists

Stick drift is a worn potentiometer. The honest fix is replacing the stick module.
But replacement costs time and money, and sometimes you just want the controller
playable tonight — including on a **PS5**, where no PC-side software can help you.

Recentring the sticks in the controller's *own* calibration data fixes drift on
**both PC and PS5**, because the correction lives in the pad, not in any driver.

The trade-off: recentring doesn't repair the wear. It shifts the reported centre
around it, which steals throw from the drifting direction. Done carelessly that
makes things worse with no undo.

**This tool's job is to make that trade-off safe and visible.**

## What it does

| Section | Reads | Writes |
|---|---|---|
| Live raw input | 8-bit stick bytes, report rate, bus type | no |
| Rest measurement | 3s capture, mean / offset / jitter / range | no |
| Baseline compare | before-vs-after after recalibrating | no |
| Calibration backup | feature report `0x05` hex + JSON export | no |
| Device info | MAC, HW/FW version from `0x09` | no |
| Recalibrate | handshake ack verification | **yes** |

## The safety model

This is the part that matters, and it's why this tool differs from others.

**Writes are volatile by default.** The calibration goes to controller RAM.
**Unplug the controller and the original calibration comes back.** Try it, and if
the stick feels worse, just unplug. There is nothing to undo because nothing
permanent happened.

Making it permanent is a separate, deliberate act:

- a distinct **"make permanent"** checkbox
- gated behind typing the word `PERMANENT`
- which unlocks controller flash (NVS) via report `0x80`
- and is labelled in the UI as the irreversible one

Every single HID transaction is printed to a log panel. Nothing happens invisibly.

## How to use

1. Plug the controller in with a **USB cable**. (Bluetooth feature-report access is
   unreliable for calibration — use USB.)
2. Open the page over `http://localhost` or HTTPS. WebHID requires a secure context.
3. Click **Connect** — you must click this yourself; browsers require a real user
   gesture to grant device access. Pick the entry whose usage is **Game Pad**.
4. **Sample 3 seconds**, hands off. This is your baseline.
5. **Read calibration (`0x05`)** and save the backup JSON. Always do this first.
6. Only then consider recalibrating. Re-sample afterwards and the comparison table
   tells you whether it actually helped.

Running locally:

```bash
python -m http.server 8777 --bind 127.0.0.1
# then open http://127.0.0.1:8777/driftlab.html
```

Or just serve `index.html` from GitHub Pages, which is already a secure context.

## Requirements

- Chromium-based browser (Chrome, Edge, Brave). WebHID is not in Firefox or Safari.
- DualSense or DualSense Edge, connected over **USB**.

## Protocol notes

Implementation follows the public protocol documented by
[dualshock-tools](https://github.com/dualshock-tools) and the Linux
`hid-playstation` driver.

**Input reports** — stick bytes:

| Connection | Report | LX | LY | RX | RY |
|---|---|---|---|---|---|
| USB | `0x01` | byte 1 | byte 2 | byte 3 | byte 4 |
| Bluetooth | `0x31` | byte 2 | byte 3 | byte 4 | byte 5 |

A perfect centre is `128`. Each raw step is about 0.8% of travel.

**Calibration command sequence:**

```
0x82  [cmd, deviceId, targetId]     cmd: 1=start 2=store 3=sample else=abort
0x83  -> [deviceId, targetId, 1, 0xff]    expected ack
targetId: 1 = centre only    2 = centre + range
```

**Permanent write** unlocks and relocks NVS:

```
0x80  [3, 2, 101, 50, 64, 12]   unlock
0x80  [3, 1]                    relock
```

**Other reports used:** `0x05` calibration data (41 bytes), `0x09` pairing info
(MAC + HW/FW version).

### Known limitation

The decoded calibration table in section 4 is **best-effort**. Stick calibration
fields are 12-bit values packed into the report, and the exact packing has varied
across firmware revisions. The raw hex dump is always shown alongside and is the
authoritative source — if the decoded numbers look implausible, trust the hex.

## Honest limits

- **This masks drift, it does not repair it.** The potentiometer is still worn.
- Heavy drift means less healthy throw to redistribute. If a recentre makes the
  stick feel worse on the good side, unplug and leave it.
- A stick that needs a large recentre is usually telling you to replace the module.
- Nothing here reaches a PS5 *console* through the PC — the fix works on PS5 only
  because it's written into the controller itself.

## Credits

Protocol and prior art by the [dualshock-tools](https://github.com/dualshock-tools)
project and the Linux `hid-playstation` driver authors. This is an independent
tool and is not affiliated with Sony.

## License

MIT — see [LICENSE](LICENSE).
