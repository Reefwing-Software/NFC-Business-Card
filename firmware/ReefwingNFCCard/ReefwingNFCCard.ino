// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Reefwing Software
// Rev C / ATtiny816 / megaTinyCore. See ../README.md before programming.
#include <Arduino.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

#if !defined(__AVR_ATtiny816__)
#error "Select ATtiny816 in megaTinyCore (non-Optiboot board)."
#endif
#if F_CPU != 1000000UL
#error "Select Tools > Clock > 1 MHz internal."
#endif
#if !defined(MILLIS_USE_TIMERNONE)
#error "Select Tools > millis()/micros() Timer > Disabled. This sketch owns RTC PIT."
#endif

// Leave false for first bring-up: animation also runs on programmer power.
// Enable only after provisioning NTAG FD_ON=00 / FD_OFF=00 and checking FD_N.
#ifndef REEFWING_REQUIRE_FIELD
#define REEFWING_REQUIRE_FIELD 0
#endif

// One tick is nominally 32 / 1024 s = 31.25 ms (internal oscillator tolerance).
constexpr uint8_t LED_ON_TICKS = 4;       // 125 ms per node
constexpr uint8_t LED_GAP_TICKS = 2;      // 62.5 ms, all LEDs off
constexpr uint8_t PATH_GAP_TICKS = 8;     // 250 ms between paths
constexpr uint8_t STARTUP_TICKS = 8;      // Start with no LED load
constexpr uint8_t LED_A_MASK = PIN4_bm | PIN5_bm | PIN6_bm | PIN7_bm;
constexpr uint8_t LED_B_MASK = PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm | PIN4_bm;
volatile uint8_t pitTicks = 0;

ISR(RTC_PIT_vect) {
  RTC.PITINTFLAGS = RTC_PI_bm;            // Write one to clear.
  ++pitTicks;
}

void allLedsOff() {
  PORTA.OUTCLR = LED_A_MASK;
  PORTB.OUTCLR = LED_B_MASK;
}

void selectLed(uint8_t node) {
  // Break before make, including transitions between different GPIO ports.
  allLedsOff();
  if (node < 4) {
    PORTA.OUTSET = uint8_t(1U << (node + 4));
  } else if (node < 9) {
    PORTB.OUTSET = uint8_t(1U << (node - 4));
  }
}

bool fieldPresent() {
  return (PORTA.IN & PIN3_bm) == 0;       // Open-drain FD_N, external pull-up.
}

void sleepOneTick() {
  // Atomic check + sleep avoids missing a wake-up between those operations.
  cli();
  const uint8_t start = pitTicks;
  while (pitTicks == start) {
    sleep_enable();
    sei();
    sleep_cpu();                        // AVR executes this before pending ISR.
    sleep_disable();
    cli();
  }
  sei();
}

bool waitTicks(uint8_t count) {
  uint8_t absentTicks = 0;
  while (count--) {
    sleepOneTick();
    if (REEFWING_REQUIRE_FIELD) {
      absentTicks = fieldPresent() ? 0 : uint8_t(absentTicks + 1);
      if (absentTicks >= 2) {            // Reject a single-sample glitch.
        allLedsOff();
        return false;
      }
    }
  }
  return true;
}

bool pulseNode(uint8_t node) {
  selectLed(node);
  const bool completed = waitTicks(LED_ON_TICKS);
  allLedsOff();
  return completed && waitTicks(LED_GAP_TICKS);
}

void setup() {
  // Disable Arduino's unused peripherals. No PWM, Serial, ADC or Wire here.
  TCA0.SPLIT.CTRLA = 0;
  TCA0.SPLIT.CTRLB = 0;
  TCB0.CTRLA = 0;
  TCD0.CTRLA = 0;
  ADC0.CTRLA = 0;
  AC0.CTRLA = 0;
  DAC0.CTRLA = 0;
  USART0.CTRLB = 0;
  SPI0.CTRLA = 0;
  TWI0.MCTRLA = 0;
  TWI0.SCTRLA = 0;

  allLedsOff();                         // Low latches before enabling outputs.
  PORTA.DIRSET = LED_A_MASK;
  PORTB.DIRSET = LED_B_MASK;
  PORTA.DIRCLR = PIN1_bm | PIN2_bm | PIN3_bm;
  PORTA.PIN1CTRL = PORT_ISC_INPUT_DISABLE_gc; // SDA, released; external pull-up
  PORTA.PIN2CTRL = PORT_ISC_INPUT_DISABLE_gc; // SCL, released; external pull-up
  PORTA.PIN3CTRL = 0;                   // FD_N input, no extra pull-up
  // Preserve PA0/UPDI. Do not change its direction, pin control or fuse.
  PORTB.DIRCLR = PIN5_bm;
  PORTB.PIN5CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTC.DIRCLR = PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm;
  PORTC.PIN0CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTC.PIN1CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTC.PIN2CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTC.PIN3CTRL = PORT_ISC_INPUT_DISABLE_gc;

  // Rev C alternate TWI location; PB0/PB1 are LEDs. TWI remains disabled.
  PORTMUX.CTRLB |= PORTMUX_TWI0_bm;
  // If adding Wire later, restore PA1/PA2 input buffers and use Wire.swap(1)
  // before Wire.begin(); Wire can configure its own pin routing.

  while (RTC.STATUS) {}
  RTC.CTRLA = 0;                       // RTC counter unused; PIT is independent.
  RTC.INTCTRL = 0;
  RTC.CLKSEL = RTC_CLKSEL_INT1K_gc;
  while (RTC.PITSTATUS) {}
  RTC.PITCTRLA = 0;
  while (RTC.PITSTATUS) {}
  RTC.PITINTFLAGS = RTC_PI_bm;
  RTC.PITINTCTRL = RTC_PI_bm;
  RTC.PITCTRLA = RTC_PERIOD_CYC32_gc | RTC_PITEN_bm;
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sei();
  waitTicks(STARTUP_TICKS);
}

void loop() {
  static uint8_t path = 0;
  if (REEFWING_REQUIRE_FIELD) {
    allLedsOff();
    uint8_t stableTicks = 0;
    while (stableTicks < 2) {
      sleepOneTick();
      stableTicks = fieldPresent() ? uint8_t(stableTicks + 1) : 0;
    }
  }

  // Enumerate all 3 x 4 x 2 input-hidden-output paths over 24 iterations.
  // D1..D3: PA4..PA6; D4: PA7; D5..D7: PB0..PB2; D8..D9: PB3..PB4.
  const uint8_t input = path % 3;
  const uint8_t hidden = 3 + (path / 3) % 4;
  const uint8_t output = 7 + path / 12;
  if (!pulseNode(input) || !pulseNode(hidden) || !pulseNode(output)) {
    path = 0;
    return;
  }
  allLedsOff();
  if (waitTicks(PATH_GAP_TICKS)) {
    path = (path + 1) % 24;
  } else {
    path = 0;
  }
}
