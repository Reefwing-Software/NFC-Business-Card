# Rev C review — 12 September 2026

Rev C incorporates the review into the schematic, PCB, sourcing and firmware requirements. Rev B files remain in `revisions/rev-b/` and the older cloud project.

| Comment | Decision |
|---|---|
| Alternate I²C pins | Retained PA1/SDA and PA2/SCL; added the required `PORTMUX.CTRLB |= PORTMUX_TWI0_bm` schematic note. PB0/PB1 remain LEDs. |
| LED current | Changed R1–R9 from 2.2 kΩ to **1 kΩ**, C21190. At a 2.0 V rail and assumed 1.7 V LED drop, the estimates are 136 µA (2.2 kΩ), 300 µA (1 kΩ), and 638 µA (470 Ω). GPIO voltage loss and the LED's actual I–V curve matter. Measure brightness, rail droop and phone range before choosing 470 Ω. “Well under a milliamp” describes the nominal 2 V case, not a guaranteed maximum: at 3 V the same simple 1 kΩ calculation gives 1.3 mA. |
| Programming link | Replaced JP1 with a **normally-open solder bridge**, two 1 mm square pads, 0.30 mm copper gap, no paste and no BOM placement. Program with it open, disconnect the fixture, then bridge manually. Wick it open for subsequent programming. Verify isolation electrically before applying fixture power. |
| VCC/VOUT | Confirmed against NXP §8.6, Figure 16. VOUT reaches VCC through closed JP1. Normal RF-powered operation needs a field; **fixture-powered I²C can work without RF** because J1 powers U1 VCC as well as U2. |
| Antenna | Retained geometry and DNP C1. Ideal resonance with 50 pF requires 2.75 µH. If measured L were 2.3 µH, ideal total capacitance would be about 59.9 pF, leaving roughly 9.9 pF before subtracting stray capacitance. This is a tuning illustration, not an independently validated inductance estimate or a C1 value to populate. |
| FD | Added **FD_N**, U1.4 → U2.2/PA3, with R12 = **100 kΩ**, C25803, to VDD. Active-low field status; approximately 20 µA pull-up current at 2 V. Provision FD_ON=00 and FD_OFF=00. FD is not a supply supervisor. Sample its level after startup; do not depend on catching an arrival edge while the MCU is unpowered. |
| Unused pins/clock/BOD | Five unused MCU pins remain: PB5 and PC0–PC3. Define their input states. Factory 20 MHz/6 is valid at 1.8 V; early division by 16 gives 1.25 MHz for lower current. Lowest BOD is 1.8 V nominal, 1.7–2.0 V range. The prototype plan disables BOD, requiring rail-sag testing; this does **not** make operation below 1.8 V valid. No physical fuse readback has been performed. |

References: [Microchip ATtiny416/816 datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATtiny416-816-DataSheet-DS40001913C.pdf), §§6.9.4.3, 10.3.3, 15.3.2, 16, 34.3 and 34.8; [NXP NTAG I²C plus datasheet](https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf), §§8.4 and 8.6, Figure 16.

## Stock verified on JLCPCB — 12 September 2026

| Positions | Part | JLCPCB | Available order quantity | Class |
|---|---|---|---:|---|
| R1–R9 | 0603WAF1001T5E, 1 kΩ ±1%, 0603 | [C21190](https://jlcpcb.com/partdetail/Uniroyal-0603WAF1001T5E/C21190) | 21,954,891 | Basic |
| R12 | 0603WAF1003T5E, 100 kΩ ±1%, 0603 | [C25803](https://jlcpcb.com/partdetail/Uniroyal-0603WAF1003T5E/C25803) | 22,499,301 | Basic |

These are dated live page readings, not reservations. The unchanged parts retain the 9 September stock audit and need rechecking at order time. The intended assembly has 25 populated placements across eight order codes. JP1, C1, L1 and J1 are excluded in the schematic. PCB-level BOM exclusions for C1, L1 and J1 still need correction and export verification; do not use an unreviewed PCB BOM for ordering.

## Verification

Structural schematic checks: 29 components, 84 pins. Library checks: all 25 populated placements match their symbol/footprint pin identities. Independent PCB checks: 27 connected nets, no unrouted connections, 0.15 mm clearance passes with the intentional winding joins excluded. EasyEDA DRC and cloud identities are recorded separately after import. Bench RF, LED, supply and QR tests remain outstanding.

## EasyEDA cloud revisions

The Rev C schematic project is saved as `Reefwing NFC Card Rev C`. The reviewed PCB is saved as `Reefwing NFC Card Rev C - Reviewed PCB`. The public repository provides native JSON imports without requiring access to the owner's cloud workspace. The PCB editor reports 29 components, 27/27 nets, and four DRC findings believed to be the intentional antenna terminal joins; the specific Rev C findings still require final review.
