# Rev D change tracker

Updated 30 September 2026. The user authorized the redesign after Rev C LED testing. The earlier hold on schematic/PCB changes is superseded.

| ID | Change | Status | Evidence / remaining work |
| --- | --- | --- | --- |
| D-001 | Rounded 85 × 55 mm board, R3 mm corners | Implemented | Native joined outline tracks/arcs; independent contour and edge-clearance checks. Gerber outline review pending. |
| D-002 | Correct D1–D9 polarity and assembly orientation | Implemented | Manufacturer 1=A, 2=K; schematic corrected; complete LED footprints rotated 180°; resistor feeds A and K is GND. JLCPCB physical assembly preview and first-article test pending. |
| D-003 | Accessible troubleshooting pads | Implemented | Two labelled 1.5 mm front pads: GND and 3V (VDD), entirely left of J1 to avoid the six-pin pogo connector extension to its right. Removed the other 23 test points. Matching schematic symbols and no paste/assembly. |
| D-004 | Assembly exclusions and artwork revision | Implemented | C1 DNP/paste disabled; L1/J1/JP1/test pads excluded; silk relieved around pads and labels; both faces identify Rev D. |

Use [Rev D review and testing guide](revisions/rev-d/README.md) for the detailed pinout, probe map, checks and remaining fabrication handoff. Rev C JSON files are preserved unchanged; source hashes are stored with Rev D.

## Test evidence motivating this revision

The user reported that UPDI upload and NFC URL reading work, but no LEDs illuminate with either the animation or simple diagnostic. Review found reversed A/K assignments in all nine Rev C custom LED symbols and matching incorrect PCB pin nets. See [Rev C polarity review](REV-C-LED-POLARITY-REVIEW.md). Physical assembly orientation has not been independently photographed or measured by this workflow.

## Still to complete before fabrication

- Native EasyEDA ERC/DRC; review antenna terminal contact findings individually.
- Exported Gerber, mask, paste and JLCPCB assembly orientation review.
- Current stock check and first assembled Rev D electrical/RF testing.

The antenna copper is unchanged. Rounded-corner and test-access changes have been checked geometrically, but their RF effect still requires measurement on hardware.
