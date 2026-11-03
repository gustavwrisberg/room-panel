# KiCad project (KiCad 10)

| File | Contents |
| --- | --- |
| `Smart_home_universal_board.kicad_pro / .kicad_sch / .kicad_pcb` | Rev 1 board, 37 × 54 mm, 2 layers |
| `libs/` | Project libraries: `EasyEDA` (encoder, SHT40, BH1750, PCA9554, buttons, C4002 socket footprint) and `Seeed_Studio_XIAO_Series` |
| `sym-lib-table`, `fp-lib-table` | Point KiCad at `libs/` via `${KIPRJMOD}`, so the project opens on any PC |
| `production/` | Fabrication Toolkit output for JLCPCB (gerber zip, BOM, CPL, IPC netlist) |

The libraries in `libs/` were extracted from the symbols and footprints embedded in
this schematic and PCB (the original impartGUI library lived only on one PC).
The EasyEDA **3D models** (`.wrl`) were not embedded and are not included, so those
five parts show without a body in the 3D viewer. Re-import them with impartGUI by
LCSC number if you need them (see `../BOM.md`).

## BOM fix (Nov 2026)

C15/C16 (10 nF) and R11/R12 (10 kΩ) had the LCSC numbers of the 100 nF and 4.7 kΩ
parts. Corrected in the schematic, PCB and `production/bom.csv`:

| Ref | Value | Was | Now |
| --- | --- | --- | --- |
| C15, C16 | 10 nF 0402 | C1525 | C15195 |
| R11, R12 | 10 kΩ 0402 | C25900 | C25744 |
