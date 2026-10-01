# Supplied EasyEDA/LCSC component definitions

These versioned `*-symbol.json` and `*-footprint.json` files are saved supplier library definitions used by Rev D. They originate from the EasyEDA/LCSC component records previously downloaded for this project. They are retained as source snapshots, rather than silently refreshed during regeneration. This is **not a current stock check**.

| LCSC code | Device / value | Rev D instances |
| --- | --- | --- |
| C710403 | NT3H2111W0FHKH | U1 |
| C2052778 | ATtiny816-MNR | U2 |
| C2286 | KT-0603R | D1–D9 |
| C21190 | 1 kΩ resistor | R1–R9 |
| C25804 | 10 kΩ resistor | R10, R11 |
| C25803 | 100 kΩ resistor | R12 |
| C107100 | 82 nF ceramic capacitor | C2 |
| C14663 | 100 nF ceramic capacitor | C3 |

C1 reuses the supplied capacitor graphics and linked C0603 footprint as an **unpopulated C0G tuning location**, with no ordered part number or fixed capacitance assigned. It is not another populated 100 nF capacitor.

The instance manifest in `revisions/rev-d/supplier-symbols.json` records each source hash, symbol UUID, linked footprint UUID and placement offset. The validator checks the actual pin definitions and PCB land geometry, in addition to schematic/PCB net agreement. Manufacturer datasheets remain the authority for polarity and IC pinout; a library UUID alone is not validation.

Third-party component definitions retain their respective licences. Their inclusion does not transfer manufacturer or distributor trademarks to this project's MIT licence.
