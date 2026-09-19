# Firmware validation

Target: Rev C, ATtiny816 (8 KiB flash, 512 bytes SRAM). Software checks only; no physical upload or fuse writes were performed.

Toolchain: Arduino CLI 1.5.1, megaTinyCore 2.6.11, bundled AVR GCC 7.3.0-atmel3.6.1-azduino7b1, macOS. Dependencies were installed in an isolated temporary directory without changing the user's Arduino IDE packages.

FQBN: `megaTinyCore:megaavr:atxy6:chip=816,clock=1internal,millis=disabled,bodmode=disabled,resetpin=UPDI`.

| Check | Result |
| --- | --- |
| Default sketch, warnings set to all | PASS: 792 bytes flash, 2 bytes static RAM; no compiler warnings |
| Optional FD gating, `compiler.cpp.extra_flags=-DREEFWING_REQUIRE_FIELD=1` | PASS: 832 bytes flash, 2 bytes static RAM; no compiler warnings |
| Incorrect `millis=enabled` configuration | Correctly rejected with an instruction to disable millis/micros |
| GPIO mapping review | D1–D9 match Rev C PA4–PA7/PB0–PB4 LED nets; PA0/UPDI is not modified |

RAM figures are static allocation, not measured peak stack usage. Compiler success does not validate timing, current consumption, rail stability, flash programming, fuse values, FD behaviour or NFC interoperability.

Before distributing cards, verify all nine LEDs and one-at-a-time operation on external 3 V power, upload verification and fuse readback, then NFC startup, repeated taps, brightness, harvested-rail sag/recovery and URL reading on representative phones. If using field gating, provision and measure FD_N behaviour separately. No NDEF or tag-register writes are implemented in this application.
