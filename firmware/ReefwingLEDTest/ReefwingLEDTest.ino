// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Reefwing Software
// Rev C wiring test: D1 through D9, one LED at a time, forever.
// Test on external 3 V with JP1 OPEN and no NFC field.
// Same Arduino settings as ReefwingNFCCard: ATtiny816, 1 MHz internal,
// millis/micros disabled, UPDI retained. No RTC, sleep, Wire or Serial.
#include <Arduino.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#if !defined(__AVR_ATtiny816__)
#error "Select ATtiny816 in megaTinyCore (non-Optiboot)."
#endif
#if F_CPU != 1000000UL
#error "Select Clock > 1 MHz internal."
#endif
#if !defined(MILLIS_USE_TIMERNONE)
#error "Select millis()/micros() Timer > Disabled."
#endif

// Explicit pin order matches the Rev C schematic.
const uint8_t ledPins[] = {
  PIN_PA4, PIN_PA5, PIN_PA6, // D1, D2, D3: input nodes
  PIN_PA7, PIN_PB0, PIN_PB1, PIN_PB2, // D4-D7: hidden nodes
  PIN_PB3, PIN_PB4          // D8, D9: output nodes
};
const uint8_t ledCount = sizeof(ledPins) / sizeof(ledPins[0]);

void allOff() {
  for (uint8_t i = 0; i < ledCount; ++i) digitalWrite(ledPins[i], LOW);
}

void setup() {
  // Busy-wait timing needs neither interrupts nor a peripheral timer.
  cli();
  for (uint8_t i = 0; i < ledCount; ++i) {
    digitalWrite(ledPins[i], LOW);
    pinMode(ledPins[i], OUTPUT);
  }
  // PA0/UPDI and the tag's I2C/FD pins are left alone.
}

void loop() {
  for (uint8_t i = 0; i < ledCount; ++i) {
    allOff();
    digitalWrite(ledPins[i], HIGH);
    _delay_ms(500);       // CPU busy-wait: independent of RTC and millis().
    digitalWrite(ledPins[i], LOW);
    _delay_ms(150);
  }
  _delay_ms(1000);        // Distinct pause before D1 starts the next sweep.
}
