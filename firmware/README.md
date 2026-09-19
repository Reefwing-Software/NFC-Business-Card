# Rev C Arduino firmware

Open [ReefwingNFCCard/ReefwingNFCCard.ino](ReefwingNFCCard/ReefwingNFCCard.ino) in Arduino IDE. This is the ATtiny816 LED animation, not AI inference. It does not write the NFC URL. Compilation is checked; hardware operation is not yet tested.

## Arduino setup

Install **megaTinyCore by Spence Konde** through Boards Manager, adding `https://drazzy.com/package_drazzy.com_index.json` to Additional Boards Manager URLs if needed. Tested with megaTinyCore **2.6.11** and Arduino CLI **1.5.1** on macOS.

| Tools menu | Selection |
| --- | --- |
| Board | megaTinyCore 20-pin family containing ATtiny816, **without Optiboot** |
| Chip | ATtiny816 |
| Clock | **1 MHz internal** |
| millis()/micros() Timer | **Disabled** |
| BOD mode when Active/Sleeping | **Disabled/Disabled**, prototype setting |
| UPDI/Reset pin function | **UPDI (no reset pin)** |
| Startup time | 8 ms |
| WDT timeout / window | Disabled |
| Programmer | **SerialUPDI – SLOW: 57600 baud** for initial bring-up |
| Port | The UPDI Friend serial port |

Other settings can remain at defaults. BOD voltage has no effect when BOD is disabled. The sketch rejects a wrong chip, clock or enabled Arduino millis timer at compile time. These settings supersede earlier advice to leave millis enabled or manually select 1.25 MHz. Let megaTinyCore configure 1 MHz (16 MHz oscillator divided by 16).

## Upload with the UPDI Friend and probe clip

1. Disconnect USB. Open **JP1**, using solder wick if previously bridged, and verify isolation with a meter. Keep the card away from NFC readers.
2. Select **3 V power and logic** on the UPDI Friend. Connect three adjacent clip contacts as shown below. Leave unused clip wires disconnected and unused tips clear of components/exposed copper. Verify continuity and orientation; clip header order is not a pinout guarantee.

| Programmer | Card |
| --- | --- |
| GND | J1.1, square GND pad |
| Voltage output, 3 V selected | J1.2, 3V0 / VDD |
| UPDI | J1.3, UPDI / PA0 |

3. Connect USB and select the port. Run **Tools → Burn Bootloader** once to apply the fuse settings. With the non-Optiboot board this configures fuses rather than installing a serial bootloader. It can erase existing firmware/data. Repeat after changing fuse settings, then upload again. Keep PA0 as UPDI.
4. Select **Sketch → Upload Using Programmer** and check the upload/verification log. Actual fuse readback and successful programming still need to be verified on your board.
5. The default sketch should animate on programmer power after approximately 250 ms. Check all nine LEDs, one at a time.
6. Unplug USB and remove the clip, then bridge **JP1 only**. Test with an NFC phone. Leave C1 unpopulated; J1 and L1 are PCB copper features. Never short the antenna terminals.

Reopen JP1 before future uploads. If the serial port does not appear, consult the [UPDI Friend guide](https://learn.adafruit.com/adafruit-updi-friend?view=all) and macOS driver instructions. Close Serial Monitor before uploading. Check contact alignment, ground, 3 V, chip selection and JP1 before changing programming speed. No programmer was contacted during our compilation checks.

## Animation and power

The sketch visits all 24 input–hidden–output combinations. Each node is lit for about 125 ms, with 62.5 ms all-off gaps and a 250 ms pause between paths. Timing uses the internal low-power oscillator and is approximate.

| LEDs | MCU GPIO | U2 package pins |
| --- | --- | --- |
| D1–D3: input | PA4, PA5, PA6 | 5, 6, 7 |
| D4–D7: hidden | PA7, PB0, PB1, PB2 | 8, 14, 13, 12 |
| D8–D9: output | PB3, PB4 | 11, 10 |

The CPU sleeps in power-down between RTC periodic interrupts; GPIO retains the selected LED state. Unused analog peripherals and PWM timers are disabled, unused input buffers are disabled, and PA0/UPDI is preserved. All LEDs switch off before selecting the next. Resistors set peak current; timing changes duty cycle.

The startup pause removes LED load temporarily, but is not a voltage measurement. Disabled BOD is a prototype choice needing harvested-rail startup, sag and recovery measurements. Behaviour below the specified MCU supply range is not guaranteed. The application writes no nonvolatile memory.

## Field detection and NFC URL

FD_N is an input on PA3 with an external 100 kΩ pull-up. **By default it does not gate animation**, allowing fixture tests without RF. In normal use animation starts with the harvested rail.

After provisioning and verifying NTAG **FD_ON=00 / FD_OFF=00**, set `REEFWING_REQUIRE_FIELD` to `1` to enable optional gating. It waits for two low samples before each path and aborts a timed step after two consecutive high samples. Without RF this mode deliberately shows no animation on programmer power. Validate behaviour with phones and RF protocol states; FD is not power-good. The sketch does not configure the tag.

The alternate TWI route PA1/SDA and PA2/SCL is selected, but I²C stays disabled. If adding Wire, restore these input buffers and call `Wire.swap(1)` before `Wire.begin()` so the library does not select the LED pins.

Write `https://www.reefwing.com.au/` using the provisioning sketch below, or separately as an **NDEF URI record** using an NFC writing app. Uploading the animation sketch does not write that record or provision FD. Check URL reading independently of animation.

## Write the NFC URL over I²C

Open [ReefwingWriteURL/ReefwingWriteURL.ino](ReefwingWriteURL/ReefwingWriteURL.ino), keeping `ProvisionURL.h` in the same folder. This separate, one-time utility replaces the tag's existing NDEF message with **https://www.reefwing.com.au/**. It targets the Rev C NT3H2111 (1K) at its default 7-bit I²C address **0x55**. It is compile-checked and host-tested, but not yet tested on a physical card.

1. Use the Arduino settings and UPDI wiring above: **JP1 open, external 3 V power, no NFC field**. Keep the supply and probe contacts stable until verification completes. The programmer supplies both the MCU and NTAG VCC.
2. Upload **ReefwingWriteURL** using the programmer. After a one-second startup delay, D4 lights briefly during provisioning.
3. Wait for **D9 to blink slowly** (half-second on/off): the URL and capability container have passed I²C read-back verification. No Serial Monitor is needed. If D1 flashes instead, count flashes between the two-second pauses using the table below; resolve the problem before proceeding.
4. With JP1 still open, upload **ReefwingNFCCard** to restore the animation. Reprogramming the MCU does not erase the separate NTAG EEPROM.
5. Disconnect the programmer, bridge JP1, then tap with a phone. Confirm that it offers the Reefwing website; opening the URL may require a tap/confirmation in the phone UI.

| D1 flashes | Meaning |
| --- | --- |
| 1 | I²C communication failed: check power, address, connections and pull-ups |
| 2 | RF field/lock present, or EEPROM busy/write-error status; remove RF and power-cycle before retrying |
| 3 | Unsupported/protected configuration: static locks, password protection, nonstandard capability container, SRAM mirror or pass-through mode; utility makes no protection changes |
| 4 | Written block did not match read-back; check stable power and contacts |

The writer uses PA1/SDA and PA2/SCL via `Wire.swap(1)`. It writes complete 16-byte EEPROM blocks with a 10 ms programming pause and verifies each block. It publishes the NDEF length after writing the tail. Fresh tags also receive capability container `E1 10 6D 00`; block 0 is handled specially to preserve the I²C address. Existing capability containers must match that value or be all zero. The first 32 bytes of user memory are replaced; later memory is untouched. A correctly provisioned tag incurs no further EEPROM writes on restart.

This is not a general-purpose tag formatter: locked/password-protected or differently configured tags need separate assessment. Passwords, lock bits and persistent configuration registers are not changed. FD settings are not provisioned. Field checks reduce accidental RF contention but do not replace keeping readers away throughout programming. An interrupted write can leave an empty/partial message; restore stable power and rerun, then verify by phone. Do not leave this utility installed as the card's normal firmware.

Protocol reference: [NXP NT3H2111/2211 datasheet](https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf), capability container/memory maps and I²C EEPROM/session access sections.

## Compile check

After installing the core, run from the repository root:

```sh
arduino-cli compile \
  --fqbn 'megaTinyCore:megaavr:atxy6:chip=816,clock=1internal,millis=disabled,bodmode=disabled,resetpin=UPDI' \
  --warnings all firmware/ReefwingNFCCard
```

See [VALIDATION.md](VALIDATION.md) for results. The compile command does not set fuses or upload.

Use the same compile command with `firmware/ReefwingWriteURL` to build the URL writer. Run the portable provisioning tests with:

```sh
c++ -std=c++11 -Wall -Wextra -pedantic firmware/tests/provision_url_test.cpp -o /tmp/provision_url_test
/tmp/provision_url_test
```

References: [megaTinyCore](https://github.com/SpenceKonde/megaTinyCore), [ATtiny416/816 datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATtiny416-816-DataSheet-DS40001913C.pdf).
