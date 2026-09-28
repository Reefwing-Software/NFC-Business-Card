# Rev C LED polarity review — 28 September 2026

Rev D now implements the correction; see the [Rev D design review](revisions/rev-d/README.md). This document records the original Rev C finding.

## Finding

All nine LEDs have a reversed pin-role assignment in the project schematic relative to the saved C2286 supplier symbol and the KENTO manufacturer drawing. This error propagates to the PCB net assignments. It is a design error, not something a successful upload can detect.

| Item | Pin 1 | Pin 2 |
| --- | --- | --- |
| KENTO drawing and saved supplier symbol | Anode (+), A | Cathode (−), K |
| Rev C custom schematic symbol labels | Cathode, K | Anode, A |
| Rev C PCB connections, D1–D9 | GND | Respective LED series resistor |

The intended active-high circuit is GPIO → 1 kΩ → LED anode → LED cathode → GND. The current footprint net assignment instead grounds the manufacturer's anode and drives its cathode through the resistor. If assembled to this footprint orientation, the LEDs are reverse-biased when the GPIO goes high.

Evidence:

- `libraries/C2286-symbol.json`: pin 1 explicitly named A; pin 2 named K.
- `Reefwing-NFC-Card-RevC.json`: D1–D9 custom symbols name pin 2 A and pin 1 K.
- `Reefwing-PCB-RevC.json`: D1–D9 pad 1 is GND; pad 2 is R1_2 through R9_2.
- [KENTO datasheet supplied by LCSC](https://datasheet.lcsc.com/datasheet/pdf/011ec3e8cb1e825f6961d29bc4db4c7a.pdf), second PDF page, package profile: terminal 1 is marked + and terminal 2 −. Drawing inspected visually.

## Other checks

The MCU GPIO/package mapping matches the Microchip 20-pin VQFN drawing:

| LEDs | GPIO | U2 pins |
| --- | --- | --- |
| D1–D4 | PA4–PA7 | 5, 6, 7, 8 |
| D5–D9 | PB0–PB4 | 14, 13, 12, 11, 10 |

Each MCU output connects to its corresponding 1 kΩ resistor in the PCB data. U2 pin 4 and C3 connect to VDD; U2 pin 3 and centre pad 21 connect to GND. J1 pins 1/2/3 are GND/VDD/UPDI, with UPDI reaching U2 pin 19. NTAG VCC shares VDD, and JP1 bridges VH to VDD.

The existing independent copper geometry checker was rerun against the actual Rev C PCB file (rather than its default routing-draft input). It reported 27 connected nets, no disconnected groups and no checked 0.15 mm clearance violations. Its intentional antenna exclusions remain in force; it is not native EasyEDA DRC or assembly verification.

Earlier connectivity checks expected LED pin 1 to be GND and pin 2 to be the resistor node, so they reinforced the incorrect mapping. Connectivity agreement between schematic and PCB did not validate the component polarity. Those assertions need correction as part of the eventual design fix.

## Confirm on one assembled LED first

The assembly files actually submitted and the physical LED orientation have not been inspected in this review. With all power disconnected, verify polarity on D1 using diode mode (red probe on anode, black on cathode; in-circuit readings can be affected by other paths). Check against the manufacturer's package mark or lift one terminal if the reading is ambiguous.

If D1 is reversed as predicted, rotating that LED 180 degrees on its existing pads would connect its physical anode to the resistor and cathode to ground. Have one LED reworked first and rerun ReefwingLEDTest on external 3 V with JP1 open before reworking the remaining eight. Firmware inversion cannot fix this topology: the other LED terminal is ground, not VDD.

## Follow-up

Correct the schematic pin-role mapping, corresponding footprint net assignments/routing, polarity markings and assembly orientation together for the next fabrication. Update validation to check actual A/K roles against the source component definition. Preserve Rev C as the tested baseline. No schematic, PCB, firmware or assembly file has been changed by this review.
