# PCB silkscreen artwork — 11 September 2026

The supplied `nfc-card-both.png` is the visual reference. The published Rev C PCB file is `../Reefwing-PCB-RevC.json`. It contains native TopSilkLayer (3) and BottomSilkLayer (4) geometry, not merely a presentation mockup.

Front: book title and subtitle, David Such, @reefwing, website, 3–4–2 neural-network links and labels, programming-pad labels. The mobile number has been removed. Electronics were moved below the contact text and rerouted. Back: vector trace of the supplied Reefwing logo, business descriptor, website, website QR, NFC-wave motif and no-battery wording. The programming pads remain on the front; the back explicitly says so rather than depicting nonexistent back pads.

QR payload: `https://www.reefwing.com.au/`. ReportLab generated a 29×29 module QR with M error correction; module pitch 0.65 mm, with a four-module quiet zone (24.05 mm total square). Camera decoding and physical scan verification are still pending. Native Vision decoder checks could not execute successfully in this environment.

Bottom geometry is mirrored about the board centre for correct back-side reading. The preview presents the back as seen by a viewer, not as transparent top-down editor geometry.

The bottom logo now uses the approved `Reefwing_Studios-restored.png`, including the complete g, Studios wording and bird standing on the S. This is an AI-assisted restoration of the supplied PNG, approved by the user. It is converted to monochrome at grayscale threshold 155, cropped only to the ink bounding box, and uniformly scaled to fit 35 × 17 mm. No lettering is substituted and no logo elements are repositioned during conversion. The native silkscreen uses merged pixel-run polygons; fine photographic detail may not survive physical printing.

The earlier reconstructed Software logo has been replaced at the user's request by the approved restored PNG artwork. Silkscreen is native geometry, not editable EasyEDA text fields. Regenerate locally with `add_silkscreen.py` to change the artwork.

The preview uses a white-mask/black-silkscreen appearance. Antenna copper is shown in muted gold for orientation; this does not add antenna solder-mask openings or specify a manufacturing finish. The preview's rounded card corners are illustrative: the actual board outline remains rectangular 85×55 mm. Preview component bodies and reference labels are schematic depictions; inspect EasyEDA for exact assembly geometry.

Minimum neural-link stroke: 0.15 mm, clipped around top-side pad envelopes with 0.3 mm margins. Full silkscreen-to-mask/via clearance and minimum printable logo/text features must be reviewed before fabrication. Do not use this draft as a manufacturing release.

The initial public repository contains the native design and artwork preview. Local generation scripts and their intermediate inputs are not included in this snapshot. Edit the imported PCB in EasyEDA; the vector lettering is not editable as ordinary text fields.

EasyEDA solid-region limitation reference: https://easyeda.com/forum/topic/Support-for-M-ove-in-SOLIDREGION-in-PCB-Editor-281ec9cf33124976811d97ed2a0f5dd2
