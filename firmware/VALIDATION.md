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
| ReefwingWriteURL, warnings set to all | PASS: 2498 bytes flash, 58 bytes static RAM; no compiler warnings |
| URL provisioning host tests | PASS: URI decoding, fresh CC initialization, I²C address/UID preservation, write order, already-correct no-write path, RF/busy/error rejection, protected/configuration rejection, communication failure, read-back mismatch and failed-tail recovery state |

RAM figures are static allocation, not measured peak stack usage. Compiler success does not validate timing, current consumption, rail stability, flash programming, fuse values, FD behaviour or NFC interoperability.

Before distributing cards, verify all nine LEDs and one-at-a-time operation on external 3 V power, upload verification and fuse readback, then NFC startup, repeated taps, brightness, harvested-rail sag/recovery and URL reading on representative phones. If using field gating, provision and measure FD_N behaviour separately. The animation does not write NDEF or tag registers; the separate URL utility writes the NDEF blocks and initializes a blank capability container, then clears the volatile I²C lock.

URL tests compile the actual `ProvisionURL.h` logic against a simulated tag. They do not validate electrical I²C timing, Wire transport on hardware, EEPROM behavior during supply interruption or phone interoperability. On this macOS host, the C++ test build required `-isystem /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk/usr/include/c++/v1` to locate the installed standard-library headers. The sketch uses megaTinyCore's built-in Wire library; no additional Arduino library installation is required.
