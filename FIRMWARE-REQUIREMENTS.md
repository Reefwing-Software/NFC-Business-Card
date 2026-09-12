# Rev C firmware and fixture requirements

These are implementation requirements and a startup example, not compiled or hardware-tested firmware.

- Keep PA0 (U2.19) configured for UPDI. Fixture uses regulated 3.0 V and 3.0 V logic, with JP1 open and no NFC field. Disconnect before bridging JP1.
- Verify OSCCFG selects 20 MHz. The reset prescaler is /6; use a protected clock write to /16 for a 1.25 MHz application clock. Set the build's `F_CPU` and peripheral timings accordingly.
- Prototype fuse plan: BOD ACTIVE and SLEEP disabled. Verify fuse readback in the fixture; do not blindly write an entire fuse byte or disable UPDI. Characterize startup, sag and recovery before deciding whether this is acceptable for distribution. Avoid MCU or tag EEPROM writes during harvested operation.
- LEDs use PA4–PA7 and PB0–PB4. Clear output latches before setting directions. One LED at a time, with an all-off interval between nodes.
- Route TWI0 to PA1/SDA and PA2/SCL before enabling TWI. Existing 10 kΩ pull-ups supply the bus. Avoid TWI transactions during the animation unless needed.
- FD_N is PA3 with an external 100 kΩ pull-up. Configure it as an input without an internal pull-up. Provision NTAG FD_ON=00/FD_OFF=00 using a read-modify-write that preserves other NC_REG settings. FD low means detected field, not guaranteed rail voltage. Sample after startup and tolerate brief field-status changes.
- Unused PB5 and PC0–PC3 should be inputs with pull-ups, or have digital input buffers disabled. Do not treat PA3 as unused in Rev C.

```c
/* Illustrative bare-metal startup; requires ATtiny816 device headers. */
PORTMUX.CTRLB |= PORTMUX_TWI0_bm;
PORTA.OUTCLR = PIN4_bm | PIN5_bm | PIN6_bm | PIN7_bm;
PORTB.OUTCLR = PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm | PIN4_bm;
PORTA.DIRSET = PIN4_bm | PIN5_bm | PIN6_bm | PIN7_bm;
PORTB.DIRSET = PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm | PIN4_bm;
PORTA.DIRCLR = PIN1_bm | PIN2_bm | PIN3_bm;
PORTA.PIN3CTRL = 0; /* FD_N: external pull-up, polling initially. */
PORTB.DIRCLR = PIN5_bm;
PORTB.PIN5CTRL = PORT_PULLUPEN_bm;
PORTC.DIRCLR = PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm;
PORTC.PIN0CTRL = PORT_PULLUPEN_bm;
PORTC.PIN1CTRL = PORT_PULLUPEN_bm;
PORTC.PIN2CTRL = PORT_PULLUPEN_bm;
PORTC.PIN3CTRL = PORT_PULLUPEN_bm;
/* avr-libc protected-write helper; verified 20 MHz oscillator fuse required. */
_PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, CLKCTRL_PDIV_16X_gc | CLKCTRL_PEN_bm);
```

The lowest BOD level is nominally 1.8 V, not a guaranteed sub-1.8 V setting. Factory 20 MHz/6 already lies below the specified 5 MHz ceiling at 1.8 V. The slow clock saves current; it does not extend the guaranteed supply range. Sources and design decisions are in `REVIEW-REV-C.md`.
