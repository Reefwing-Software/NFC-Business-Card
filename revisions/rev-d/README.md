# Rev D — LED correction and test access

Design date: 28 September 2026. Native EasyEDA Standard files are [schematic](../../Reefwing-NFC-Card-RevD.json) and [PCB](../../Reefwing-PCB-RevD.json). Rev C is preserved for comparison. This is a reviewed design candidate, not a fabrication release.

![Rev D front, rendered from native PCB geometry](pcb-front.png)
![Rev D back, viewed from below](pcb-back.png)

The previews show copper through the solder mask for inspection; colours are illustrative. Thin seams between adjacent vector polygons can appear in the preview and do not represent gaps specified in the artwork.

## LED polarity correction

The KENTO KT-0603R drawing identifies **1 = anode (+), 2 = cathode (−)**. Rev C's custom symbols assigned those roles backwards. Rev D corrects the symbols and rotates each complete placed LED footprint 180° while retaining the manufacturer's pad numbers. Each anode now faces its series resistor (left in the front view); each cathode faces right and connects to GND. Rotation metadata and footprint marking geometry change together. Merely swapping net labels would not have been sufficient.

The circuit remains **GPIO → 1 kΩ → pin 1/A → pin 2/K → GND**. Existing active-high firmware remains appropriate: HIGH lights an LED. This revision does not require reworking the existing Rev C cards; it is a new board design.

Manufacturer evidence: [KENTO KT-0603R drawing, PDF page 2](../../datasheets/KT-0603R.pdf). Third-party datasheets retain their original copyright and are not relicensed under MIT.

## Corners and antenna

The outline remains **85 × 55 mm**, with four **3 mm radius** corners implemented as connected native Board Outline tracks and arcs. The four-turn antenna copper and its terminal geometry are unchanged. C1 remains unpopulated initially and has no solder paste in Rev D; do **not** short its pads. Its pads are across the antenna, not a missing series connection.

The independent validator checks the closed outline and copper-to-edge clearance. The continuous winding intentionally joins the two RF terminal nets; EasyEDA can report these as inter-net clearance errors. The validator exempts only contacts at the two antenna terminals, not arbitrary antenna routing. Native DRC and exported Gerber verification remain necessary before fabrication.

## Probe access

There are **two additional 1.5 mm diameter test pads on the front**, labelled **GND** (TP1) and **3V** (TP2). They have exposed solder mask and no solder paste and are excluded from assembly. Both pads are entirely to the **left of J1**, leaving the three unused positions of the six-pin pogo connector to its right free of new test pads.

| Marking | Reference | Measurement |
| --- | --- | --- |
| GND | TP1 | Common meter/scope reference |
| 3V | TP2 | VDD: MCU and NTAG VCC supply, downstream of JP1 |

Measure the supply directly between these two pads. The **3V** label identifies the externally powered programming/test rail; NFC-harvested operation is not regulated to 3 V and may read lower. The schematic includes both pads; [test-points.json](test-points.json) records their positions and nets. The previous 23 signal/LED test points and their branches have been removed.

For external-power testing or UPDI programming, open JP1, remove the NFC field, and apply regulated 3 V at J1/VDD with common GND. Do not feed external power into VH. Disconnect the programmer before closing JP1 for NFC operation. Do not probe the antenna with an ordinary probe when checking resonance; its capacitance changes the tuning.

## Component orientation review

| Parts | Review and Rev D disposition |
| --- | --- |
| D1–D9, KT-0603R | Manufacturer 1=A, 2=K checked; all placed footprints rotated 180° from Rev C; anode left, cathode right. |
| U1, NT3H2111W0FHKH | NXP XQFN8 **top view**, section 7.1.1 and pin table 7.2: 1 LA, 2 VSS, 3 SCL, 4 FD, 5 SDA, 6 VCC, 7 VOUT, 8 LB. Pin 1 is upper-left on this PCB; pin 8 is upper-centre. No centre solder pad is added. |
| U2, ATtiny816-MNR | Microchip **20-pin VQFN**, section 4.3, page 17: package pin mapping checked independently of SOIC. Pin 1 is lower-left on this PCB; pin 4 VDD, pin 3 and exposed pad 21 GND, pin 19 UPDI. The supplier's zero-degree footprint is rotated relative to the datasheet drawing; numbering follows the actual lands. |
| R1–R12 | Unpolarized resistors; values retained: R1–R9 1 kΩ, R10/R11 10 kΩ, R12 100 kΩ. |
| C2/C3 | Unpolarized ceramic capacitors, 82 nF / 100 nF respectively. C1 optional unpolarized tuning capacitor, DNP. |
| J1 | Square pin 1=GND, centre pin 2=VDD, pin 3=UPDI. Front-side probe contact. |
| JP1 | Normally-open copper solder bridge, pin 1=VH and pin 2=VDD. No placed component. |
| L1 | Printed coil; pad 1=ANT_A, pad 2=ANT_B. No placed component. |
| TP1–TP2 | Single-pad copper features, no assembly orientation requirement. |

C1, L1, J1, JP1 and all test pads are excluded from PCB assembly/BOM exports. The 25 populated components and eight purchased part codes are unchanged. Stock must be checked again at ordering time.

## Validation and fabrication handoff

Run `python3 revisions/rev-d/validate_rev_d.py`. [validation.json](validation.json) records schematic-to-PCB agreement, manufacturer LED roles, placement rotations, pad connections, exclusions, contour and silk relief. [pcb-clearance-report.json](pcb-clearance-report.json) and [pcb-connectivity-report.json](pcb-connectivity-report.json) record the independent copper checks.

These checks do not substitute for EasyEDA's native ERC/DRC, Gerber review or physical testing. Before ordering:

1. Import the two Rev D JSON files into a **new Rev D project** in EasyEDA Standard using File → Open → EasyEDA. Preserve the Rev C cloud project. Import the optional test-pad library if editing/replacing those footprints.
2. Run native ERC and DRC. Review the intentional winding contacts individually; do not globally waive unrelated clearance errors.
3. Export Gerbers and inspect the closed rounded outline, copper, solder-mask openings, paste exclusions and both silkscreens.
4. Export the BOM and placement file from Rev D. In the JLCPCB assembly preview, verify the physical cathode of every LED lands on **pad 2/GND/right**, and inspect U1/U2 pin-1 positions against their package drawings. Numeric rotation alone is not sufficient evidence because assembly library zero-degree conventions can differ.
5. First test one assembled card on regulated 3 V with JP1 open using ReefwingLEDTest. Check GPIO voltage, LED anode voltage and current before testing harvested power and antenna tuning.

No native EasyEDA DRC pass, JLCPCB assembly-preview approval, or Rev D hardware pass is claimed by these files.

## Regeneration

`build_rev_d.py` derives Rev D from immutable Rev C files; `source-hashes.json` identifies that baseline. Dependencies are listed in `requirements.txt`. `render_rev_d.py` generates SVG previews from actual PCB geometry; the PNGs are rasterized from those SVGs. The independent validator does not invoke the generator.
