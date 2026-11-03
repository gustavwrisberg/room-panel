# Assembly

## 1. Solder the through-hole parts

| Ref | Part | Note |
| --- | --- | --- |
| J1 | 1×5 female socket, horizontal | C4002 lies flat with its antenna side facing the front |
| J3 | JST PH 8-pin (or 1×8 pin header) | Display cable |
| J4 | 1×4 female socket | SCD40 breakout cable |
| J2 | – | Leave empty on panels (motor board only) |

Check the display's pin order on its silkscreen: VCC, GND, DIN, CLK, CS, DC, RST, BUSY
must match J3 pins 1–8. Set the display's **BS switch to 0** (4-wire SPI).

## 2. Print the case

Files: `hardware/case/out/`

| Part | Qty | Orientation | Notes |
| --- | --- | --- | --- |
| `front_shell.stl` | 1 | Front face down | No supports needed except optionally for the USB slot |
| `back_plate.stl` | 1 | Flat side down | |
| `button_cap.stl` | 4 | Flange down | |
| `knob.stl` | 1 | Top down | Print a test first: shaft hole fit is printer-dependent |

PLA or PETG, 0.2 mm layers, 3 walls, 20 % infill. Avoid black filament in front
of the radar window (some black pigments contain carbon and weaken 24 GHz).

### Before printing: CHECK these values

Open `hardware/case/room_panel_case.py` and compare with your real parts. The
easiest way is to export the PCB from KiCad as STEP (File → Export → STEP) and
overlay it on `out/assembly.step` in Fusion/Onshape/FreeCAD.

- `KNOB`, `BUTTONS`, `RADAR`, `LIGHT`, `SHT40`, `USB_X`: positions on the PCB
- `PCB_GAP`: distance from the front panel to the PCB (sets button-cap length)
- `VIEW_OFFSET_X`: active area offset on the Waveshare module
- CO₂ cradle size in `back_plate()`
- Knob shaft type and diameter (`knob()`)

Re-run `python3 room_panel_case.py` after changes (`pip install cadquery`).

## 3. Put it together

1. Drop the four button caps into the front panel holes from the inside.
2. Lay the display module face-down between the four corner locators.
3. Place the PCB on its four corner shelves (components facing the front panel);
   the knob shaft goes through its hole.
4. Plug in the display cable (J3) and the CO₂ cable (J4); lay the CO₂ breakout in
   the cradle on the back plate, sensor opening facing the display.
5. Screw the back plate on with 4 × M2.5 × 8 self-tapping screws.
6. Press the knob onto the shaft.
7. Hang on two wall screws through the keyhole slots; USB-C exits at the bottom.

## Vents

- Top and bottom edge behind the display: air for the CO₂ sensor.
- Bottom edge under the SHT40: fresh air for fast open-window detection.
Keep them uncovered.
