# Firmware and Home Assistant setup

## Flash

1. Install the ESPHome add-on (or `pip install esphome`).
2. Copy `firmware/secrets.example.yaml` to `firmware/secrets.yaml` and fill in Wi-Fi
   and a fresh API key (`openssl rand -base64 32`).
3. Edit the `substitutions:` at the top of `living-room-panel.yaml` to match your
   entity names (light, blinds, scripts, electricity price sensor).
4. First flash over USB-C: `esphome run firmware/living-room-panel.yaml`.
   Later updates go over Wi-Fi.

The config validates with ESPHome 2026.10. The C4002 radar uses DFRobot's
community component (`github://cdjq/esphome@dev`).

## Allow the panel to control Home Assistant

Settings → Devices & services → ESPHome → *Living Room Panel* → Configure →
tick **Allow the device to perform Home Assistant actions**.
Without this the buttons and knob do nothing.

## Controls

| Control | Short press | Long press |
| --- | --- | --- |
| Knob turn | Dim lights ±5 % or move blinds ±10 % | – |
| Knob press | Switch knob between lights and blinds | – |
| Button 1 – Lights | Toggle | 100 % |
| Button 2 – Blinds | Open/close | 50 % |
| Button 3 – Scene | `script.living_room_scene_next` | `script.living_room_auto` |
| Button 4 – All off | `script.living_room_all_off` | `script.living_room_night` |

Create the four scripts in Home Assistant (or change the substitutions).

## Display

- **Status page** (default): temperature, humidity, CO₂ (with "Air out!" over
  1000 ppm), time and electricity price. Refreshes once a minute.
- **Control page**: appears when someone is within 1 m of the panel (radar
  distance) or any control is used; shows light level and blind position, and
  which one the knob controls. Returns to status after 30 s.

## Entities the panel provides

Presence, Someone at panel, Temperature, Humidity, Illuminance, CO2, radar
distances, the four buttons, and a "Radar calibrate room" switch (run it once
with the room empty).

## Useful automations

- **Presence lighting**: Presence on + Illuminance below ~30 lx → lights on;
  off 5 min after presence clears.
- **Heating setback**: Presence off for 30 min → radiator valve setpoint −2 °C.
- **Open-window detection**: add a *Derivative* helper on Temperature (time
  window 2 min, unit °C/min); if it drops below −0.3 °C/min → radiator off until
  the temperature recovers.
- **Ventilation hint**: CO2 above 1000 ppm → notification.

## Pin map (XIAO ESP32-C6)

| XIAO | GPIO | Net |
| --- | --- | --- |
| D0 | 0 | EPD_BUSY |
| D1 | 1 | EPD_DC |
| D2 | 2 | KNOB_A |
| D3 | 21 | KNOB_B |
| D4 | 22 | SDA |
| D5 | 23 | SCL |
| D6 | 16 | RADAR_RX (ESP TX) |
| D7 | 17 | RADAR_TX (ESP RX) |
| D8 | 19 | EPD_SCK |
| D9 | 20 | EPD_CS |
| D10 | 18 | EPD_MOSI |
| internal | 3 / 14 | RF switch / antenna select (built-in antenna) |

| PCA9554 | Net |
| --- | --- |
| P0 | EPD_RST |
| P1 | KNOB_SW |
| P2 | BTN_LIGHTS |
| P3 | BTN_SCENE (CHECK) |
| P4 | RADAR_OUT |
| P5 | BTN_BLINDS |
| P6 | J2 spare |
| P7 | BTN_ALL_OFF (CHECK) |
