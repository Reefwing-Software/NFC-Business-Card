# Reefwing NFC Business Card

A battery-free PCB business card promoting [Embedded AI](https://nostarch.com/embedded-ai) by David Such and [Reefwing Software](https://www.reefwing.com.au/). An NFC reader field supplies energy for a nine-LED, 3–4–2 neural-network animation. The animation illustrates a network; it does not perform inference.

Inspired by [Wilson Harper's NFC business card](https://wilsonharper.net/projects/businesscard/).

## Status: Rev C prototype

The schematic and routed PCB are designed in **EasyEDA Standard**, targeting JLCPCB manufacture and assembly. These files are a work in progress, **not a manufacturing release**. No boards have been bench-tested and no working firmware is included yet.

![Front and back artwork preview](artwork/silkscreen-preview.png)

The preview is illustrative: the actual board outline is rectangular, 85 × 55 mm. Preview colours do not specify solder mask or surface finish.

## Design

- NXP NT3H2111 NTAG I²C plus with a four-turn PCB antenna and optional tuning capacitor.
- ATtiny816 with nine red LEDs, illuminated one at a time through 1 kΩ resistors.
- NFC field-detect input on PA3; alternate TWI pins PA1/PA2.
- Three front-side UPDI programming pads and a normally-open solder bridge for power isolation.
- Front and back silkscreen promoting the book and company; QR payload: `https://www.reefwing.com.au/`.

## Files

| File | Purpose |
| --- | --- |
| [Reefwing-NFC-Card-RevC.json](Reefwing-NFC-Card-RevC.json) | Native EasyEDA Standard schematic project |
| [Reefwing-PCB-RevC.json](Reefwing-PCB-RevC.json) | Native EasyEDA Standard PCB with silkscreen |
| [footprints/](footprints/) | Native antenna, programming-pad and solder-bridge footprints |
| [REVIEW-REV-C.md](REVIEW-REV-C.md) | Review decisions, component changes and dated sourcing checks |
| [FIRMWARE-REQUIREMENTS.md](FIRMWARE-REQUIREMENTS.md) | Firmware and programming-fixture requirements; illustrative code only |
| [artwork/README.md](artwork/README.md) | Artwork geometry and preview limitations |

In EasyEDA Standard, use **File → Open → EasyEDA…** to import the schematic or PCB JSON. The design files contain their placed symbols and footprints. The separate footprint JSON files can be imported as PCB libraries.

## Checks and remaining work

Local structural checks reported 29 components, 84 pins, matching schematic/PCB connectivity, and no unconnected nets. Independent clearance checks passed at 0.15 mm with intentional antenna winding joins excluded. Native EasyEDA reports four DRC findings associated with the antenna; the exact Rev C findings still need final review. These checks are not electrical, RF or manufacturing validation.

Before fabrication:

- Correct and verify PCB BOM exclusions: C1 is DNP; L1, J1 and JP1 are copper features, not assembly placements. C1, L1 and J1 currently retain PCB-level BOM flags and must be excluded from any assembly export. The schematic exclusions are set.
- Review Gerbers, solder mask, paste, component orientation, silkscreen clearances and JLCPCB assembly preview.
- Recheck stock for all eight populated order codes. Stock readings in the review are dated observations, not reservations.
- Implement and test firmware, verify fuses, and build the regulated 3.0 V UPDI fixture. Program with JP1 open and no NFC field; disconnect the fixture before bridging JP1.
- Measure antenna resonance and tune C1 as needed; test harvested-rail startup and sag, LED brightness, phone compatibility and physical QR scanning.

The Medium design-process article is being prepared separately and is not yet published.

## Licensing

This project is released under the [MIT License](LICENSE). Copyright © 2026 Reefwing Software. Third-party component definitions retain their respective licences, and trademark rights in branding are not granted by this licence.
