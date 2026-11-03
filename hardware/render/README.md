# 3D render

Makes `docs/pcb_render.png`, `docs/case_closed.png` and `docs/case_exploded.png` straight from the KiCad board file and the case STLs.

- `build.py`: reads `../kicad/Smart_home_universal_board.kicad_pcb` (outline, copper, pads, silkscreen, part positions), places the STEP models and writes `scene.glb` and `scene.json`.
- `stepcolor.py`: loads a STEP file and keeps its colours.
- `index.html` + `shot.js`: three.js scene rendered with Playwright. Adds the e-paper status page, the cables, the SCD41 breakout and the case (`../case/out/*.stl`). `mode=pcb`, `mode=case` or `mode=exploded`.

The XIAO, the C4002 module and the Waveshare display module are simple stand-ins built from their outlines. The SCD40 breakout sits behind the display in the case and isn't shown.

```sh
pip install cadquery trimesh shapely mapbox_earcut sexpdata
npm i three@0.170.0 playwright
# KiCad standard models (resistors, caps, JST PH, pin sockets):
git clone --depth 1 --filter=blob:none --sparse https://github.com/KiCad/kicad-packages3D k3d
(cd k3d && git sparse-checkout set --no-cone /Resistor_SMD.3dshapes/R_0402_1005Metric.step \
  /Capacitor_SMD.3dshapes/C_0402_1005Metric.step /Capacitor_SMD.3dshapes/C_0805_2012Metric.step \
  /Connector_JST.3dshapes/JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical.step \
  /Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step \
  /Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x05_P2.54mm_Horizontal.step)
python3 build.py ../kicad/Smart_home_universal_board.kicad_pcb k3d ../kicad/libs/EasyEDA.3dshapes .
(cd .. && python3 -m http.server 8765 &)      # serve hardware/ so ../case/out is reachable
node shot.js pcb_render.png    "mode=pcb&c=93,-236,188&t=93,-149,3&fov=25" 1600 800 2
node shot.js case_closed.png   "mode=case&c=60,-95,300&t=93,-147,0&fov=26" 1600 900 2
node shot.js case_exploded.png "mode=exploded&ef=64&eb=46&c=30,175,240&t=93,-147,-2&fov=31" 1600 1000 2
```
