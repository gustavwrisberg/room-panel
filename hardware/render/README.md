# 3D render

Makes `docs/pcb_render.png` straight from the KiCad board file.

- `build.py`: reads `../kicad/Smart_home_universal_board.kicad_pcb` (outline, copper, pads, silkscreen, part positions), places the STEP models and writes `scene.glb` and `scene.json`.
- `stepcolor.py`: loads a STEP file and keeps its colours.
- `index.html` + `shot.js`: three.js scene rendered with Playwright. Adds the e-paper status page and the display cable.

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
python3 -m http.server 8765 &
node shot.js pcb_render.png "c=93,-236,188&t=93,-149,3&fov=25" 1600 800 2
```
