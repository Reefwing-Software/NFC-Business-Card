# Rev C firmware and fixture requirements

The implemented sketch is [firmware/ReefwingNFCCard/ReefwingNFCCard.ino](firmware/ReefwingNFCCard/ReefwingNFCCard.ino). Follow the [firmware guide](firmware/README.md) for exact Arduino settings and upload steps. It is compile-checked, but has not been uploaded or bench-tested here.

- Select ATtiny816, **1 MHz internal**, and **millis/micros disabled**. megaTinyCore configures the clock; the sketch owns RTC PIT and sleeps in power-down between ticks. This supersedes the earlier 1.25 MHz bare-metal proposal.
- Keep PA0 configured for UPDI. Use the UPDI Friend's 3 V setting, JP1 open, and no NFC field. Disconnect before bridging JP1. Verify fuse readback on hardware; never disable UPDI.
- Prototype fuse plan: BOD disabled in active/sleep, watchdog disabled, 8 ms startup. Test rail sag and recovery before distribution. Disabling BOD does not extend the MCU's guaranteed supply range.
- LEDs use PA4–PA7 and PB0–PB4. Clear latches before enabling outputs; light one LED at a time with all-off intervals.
- TWI is routed to PA1/SDA and PA2/SCL but left disabled. The application makes no I²C transactions and writes no EEPROM. Program the NDEF URL separately over RF.
- FD_N is PA3 with an external 100 kΩ pull-up. Default animation runs whenever powered, including fixture tests without RF. Optional field gating requires verified NTAG FD_ON=00 / FD_OFF=00 configuration, preserving other NC_REG settings. The sketch does not provision the tag. FD is not a supply supervisor.
- Disable unused digital input buffers on PB5 and PC0–PC3. Leave externally pulled-up I²C lines released and preserve UPDI.

[REVIEW-REV-C.md](REVIEW-REV-C.md) records earlier hardware decisions; its 1.25 MHz discussion is historical. Use the Arduino settings above.
