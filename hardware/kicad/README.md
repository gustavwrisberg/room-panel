# KiCad project (KiCad 10)

| File | Contents |
| --- | --- |
| `Smart_home_universal_board.kicad_pro / .kicad_sch / .kicad_pcb` | Rev 1 board, 37 × 54 mm, 2 layers |
| `libs/EasyEDA.*` | The parts this board uses from the impartGUI EasyEDA library (symbols, footprints, 3D models): encoder, SHT40, BH1750, PCA9554, buttons, C4002 socket footprint |
| `libs/Seeed_Studio_XIAO_Series.*` | XIAO ESP32-C6 symbol and footprint |
| `sym-lib-table`, `fp-lib-table` | Point KiCad at `libs/` via `${KIPRJMOD}`, so the project opens on any PC |
| `production/` | Fabrication Toolkit output for JLCPCB (gerber zip, BOM, CPL, IPC netlist) |

`libs/EasyEDA.*` is copied from the original library (`E:\KicadLibrary`), trimmed
to the parts on this board. The XIAO library was extracted from the copy embedded
in the schematic and PCB.

The footprints load their 3D models from `${KICAD_3RD_PARTY}/EasyEDA.3dshapes/`.
On another PC, copy `libs/EasyEDA.3dshapes` into the folder that
`KICAD_3RD_PARTY` points to (Preferences → Configure Paths) to see them in the
3D viewer. Fabrication is not affected.

## BOM fix (Nov 2026)

C15/C16 (10 nF) and R11/R12 (10 kΩ) had the LCSC numbers of the 100 nF and 4.7 kΩ
parts. Corrected in the schematic, PCB and `production/bom.csv`:

| Ref | Value | Was | Now |
| --- | --- | --- | --- |
| C15, C16 | 10 nF 0402 | C1525 | C15195 |
| R11, R12 | 10 kΩ 0402 | C25900 | C25744 |
