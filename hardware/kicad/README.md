# KiCad project (KiCad 10)

- `Smart_home_universal_board.kicad_pro / .kicad_sch / .kicad_pcb` – rev 1 board, 37 × 54 mm, 2 layers
- `production/` – Fabrication Toolkit output sent to JLCPCB (gerber zip, BOM, CPL, IPC netlist)

The imported LCSC/EasyEDA parts (BMQ22 encoder, SHT40, BH1750, PCA9554, buttons,
XIAO) come from a separate library (`EasyEDA.kicad_sym` / `EasyEDA.pretty` /
`EasyEDA.3dshapes`) that is not in this folder. Re-import them with impartGUI by
LCSC number (see `../BOM.md`) or add the library here.

Known issue in the source files: the LCSC fields for C15/C16 (should be 10 nF,
C15195) and R11/R12 (should be 10 kΩ, C25744) still point to C1525 / C25900.
