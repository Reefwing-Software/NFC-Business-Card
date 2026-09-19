// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Reefwing Software
// ONE-TIME NT3H2111 provisioning: https://www.reefwing.com.au/
// JP1 OPEN; external regulated 3 V on J1; NO NFC field. See ../README.md.
// Replaces the existing NDEF message. Upload ReefwingNFCCard afterwards.
#include <Arduino.h>
#include <Wire.h>
#include <util/delay.h>
#include "ProvisionURL.h"

#if !defined(__AVR_ATtiny816__) || F_CPU != 1000000UL
#error "Select ATtiny816, non-Optiboot, 1 MHz internal in megaTinyCore."
#endif
#if !defined(MILLIS_USE_TIMERNONE)
#error "Select millis()/micros() Timer > Disabled, as for the animation sketch."
#endif

class Ntag {
 public:
  bool read(uint8_t block, uint8_t *data) {
    Wire.beginTransmission(ReefwingURL::ADDRESS);
    Wire.write(block);
    if (Wire.endTransmission(true)) return false;
    _delay_us(100); // NXP requires >=50 us when clock stretching is disabled.
    if (Wire.requestFrom(ReefwingURL::ADDRESS, uint8_t(16), uint8_t(true)) != 16)
      return false;
    for (uint8_t i = 0; i < 16; ++i) data[i] = Wire.read();
    return true;
  }
  bool write(uint8_t block, const uint8_t *data) {
    Wire.beginTransmission(ReefwingURL::ADDRESS);
    Wire.write(block);
    Wire.write(data, 16);
    const uint8_t error = Wire.endTransmission(true);
    // No ACK polling: commands during the EEPROM write can corrupt memory.
    _delay_ms(10);
    return error == 0;
  }
  bool session(uint8_t reg, uint8_t &value) {
    Wire.beginTransmission(ReefwingURL::ADDRESS);
    Wire.write(0xFE);
    Wire.write(reg);
    if (Wire.endTransmission(true)) return false;
    _delay_us(100);
    if (Wire.requestFrom(ReefwingURL::ADDRESS, uint8_t(1), uint8_t(true)) != 1)
      return false;
    value = Wire.read();
    return true;
  }
  bool release() {
    Wire.beginTransmission(ReefwingURL::ADDRESS);
    Wire.write(0xFE);
    Wire.write(6);    // NS_REG
    Wire.write(0x40); // Modify only I2C_LOCKED, a volatile session bit.
    Wire.write(0);
    return Wire.endTransmission(true) == 0;
  }
};

uint8_t outcome = ReefwingURL::BUS;
void ledsOff() { PORTA.OUTCLR = 0xF0; PORTB.OUTCLR = 0x1F; }

void setup() {
  ledsOff();
  PORTA.DIRSET = 0xF0;
  PORTB.DIRSET = 0x1F;
  // Leave PA0/UPDI alone; PA1/PA2 have external 10k I2C pull-ups.
  PORTA.PIN1CTRL = 0;
  PORTA.PIN2CTRL = 0;
  PORTA.PIN3CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTB.PIN5CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTC.PIN0CTRL = PORTC.PIN1CTRL = PORTC.PIN2CTRL =
      PORTC.PIN3CTRL = PORT_ISC_INPUT_DISABLE_gc;
  _delay_ms(1000);
  if (!Wire.swap(1)) return; // Alternate TWI: PA1 SDA / PA2 SCL, not LED PB0/1.
  Wire.begin();
  Wire.setClock(50000);
  PORTA.OUTSET = PIN7_bm;    // D4 steady while provisioning.
  Ntag tag;
  outcome = ReefwingURL::provision(tag);
  if (!tag.release() && outcome == ReefwingURL::OK) outcome = ReefwingURL::BUS;
  Wire.end();
  ledsOff();
}

void loop() {
  if (outcome == ReefwingURL::OK) {
    PORTB.OUTSET = PIN4_bm;  // D9: slow blink = verified success.
    _delay_ms(500);
    ledsOff();
    _delay_ms(500);
  } else {
    // D1: count flashes, then a two-second pause. No automatic write retries.
    for (uint8_t i = 0; i < outcome; ++i) {
      PORTA.OUTSET = PIN4_bm;
      _delay_ms(200);
      ledsOff();
      _delay_ms(200);
    }
    _delay_ms(2000);
  }
}
