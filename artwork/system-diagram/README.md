# NFC card system block diagram

- `reefwing-nfc-system.png`: 3600 × 2240 pixels, suitable for the Medium article.
- `reefwing-nfc-system.svg`: editable vector master.
- `generate.py`: reproducible SVG generator (Python standard library).

Suggested caption: **The Reefwing NFC business card harvests energy from a phone through its PCB antenna and NTAG I²C plus. The ATtiny816 uses that energy to animate nine LEDs, while the NTAG stores the website URL. Opening JP1 isolates the harvesting output during external 3 V programming.**

The diagram shows functional connections. The VCC return crosses VOUT with a bridge symbol, indicating no connection at that crossing; JP1 is the only intended link from VOUT to the VDD rail. Both chips use the same VDD rail in NFC and programming modes. All grounds are common; decoupling and the 10 kΩ I²C pull-ups are omitted for clarity.

I²C uses the alternate PA1/PA2 route. The URL provisioning sketch uses it; the normal animation sketch leaves I²C disabled. FD is wired to PA3, but animation gating is optional and needs the corresponding NTAG configuration. The animation and URL writer are separate sketches uploaded in sequence, not concurrent applications. The LED pattern illustrates a neural network; it performs no AI inference.

Sources supplied by the user:

- [NXP NT3H2111/2211 datasheet](../../datasheets/NT3H2111_2211_data_sheet.pdf): block diagram, pinning, and §8.6 energy harvesting. The 2 V / 5 mA figure is typical, not a guaranteed power budget.
- [Microchip ATtiny417/814/816/817 DS40002288A](../../datasheets/ATtiny417-814-816-817-DataSheet-DS40002288A.pdf): device summary, block diagram and pin multiplexing. The 1 MHz operating clock is this project's firmware choice.
- [Rev C schematic](../../Reefwing-NFC-Card-RevC.json), [hardware review](../../REVIEW-REV-C.md) and [firmware](../../firmware/README.md): board-specific wiring and operating modes.

Original diagram released under the repository's MIT licence. Hardware remains a prototype requiring bench validation.
