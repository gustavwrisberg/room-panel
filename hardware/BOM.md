# Bill of materials – one room panel

Prices are approximate (Nov 2026), USD, excluding shipping and VAT.

| Group | Ref | Item | Part / spec | Qty | Source | Unit $ | Total $ | Notes |
|---|---|---|---|---|---|---|---|---|
| PCB assembly | PCB | Main board (2-layer 37x54 mm) | JLCPCB PCB prototype | 1 | JLCPCB | 0.80 | 0.80 | $4.00 for 5 boards |
| PCB assembly | PCBA | SMT assembly incl. all SMD parts + XIAO ESP32-C6 | JLCPCB Economic PCBA top side | 1 | JLCPCB | 16.31 | 16.31 | $81.56 for 5 boards; includes U1 U2 U4 U5 SW1-SW5 and passives |
| Plug-in modules | J1 | mmWave presence radar | DFRobot Fermion C4002 (SEN0691) | 1 | DFRobot / Mouser / DigiKey | 12.00 | 12.00 | Price estimate; check DFRobot store |
| Plug-in modules | J3 | E-paper display 2.9in 296x128 B/W with driver board | Waveshare 2.9inch e-Paper Module (V2) | 1 | TinyTronics / TME / Waveshare | 20.00 | 20.00 | ~€19 at TinyTronics, $17.31 at TME; set BS switch to 0 (4-wire SPI) |
| Plug-in modules | J4 | CO2 sensor breakout (GND VDD SCL SDA) | SCD40 breakout 4-pin 2.54 mm | 1 | AliExpress | 20.00 | 20.00 | Price varies a lot ($15-35); bare SCD40 is ~$18 |
| Connectors | J1 | Radar socket | Female pin socket 1x5 2.54 mm horizontal | 1 | LCSC / AliExpress | 0.15 | 0.15 | Hand-solder |
| Connectors | J3 | Display connector | JST PH 2.0 8-pin vertical (B8B-PH-K) | 1 | LCSC | 0.10 | 0.10 | Or 1x8 2.54 mm pin header if the display cable ends in Dupont |
| Connectors | J4 | CO2 breakout socket | Female pin socket 1x4 2.54 mm vertical | 1 | LCSC / AliExpress | 0.10 | 0.10 | Hand-solder |
| Connectors | J2 | Motor board socket | Female pin socket 2x5 2.54 mm | 0 | LCSC | 0.20 | 0.00 | Blind version only; leave empty on panels |
| Cables | - | Display cable | PH2.0 8-pin to PH2.0 8-pin 10-15 cm | 1 | AliExpress | 0.50 | 0.50 | Waveshare's included cable ends in Dupont; buy PH-PH or use pin header on J3 |
| Cables | - | CO2 cable | 4-wire Dupont female-female 15 cm (or male-female) | 1 | AliExpress | 0.20 | 0.20 | Breakout sits behind display |
| Power | - | USB-C cable | USB-C 1 m | 1 | Any | 2.00 | 2.00 |  |
| Power | - | USB power supply | 5 V 1 A USB charger | 1 | Any | 4.00 | 4.00 | Reuse an old phone charger if available |
| Case | - | 3D-printed parts | PLA or PETG ~55 g (front shell + back plate + 4 button caps + knob) | 1 | Own printer | 1.20 | 1.20 | Files in hardware/case |
| Case | - | Case screws | M2.5 x 8 self-tapping (or M2.5 + heat inserts) | 4 | Any | 0.05 | 0.20 | Back plate to front shell |
| Case | - | Wall screws + plugs | 3.5 x 25 mm screw + plug | 2 | Any | 0.10 | 0.20 | Keyhole mounting |

**Total per panel: $77.76**

JLCPCB order (5 boards): PCB $4.00 + PCBA $81.56. Assembled parts: XIAO ESP32-C6 (C27675191), SHT40 (C54946589), BH1750FVI-TR (C78960), PCA9554PW (C17230), BMQ22-N1A1-2012-A encoder (C52740763), TS-1187A buttons (C318884), 10 µF (C15850), 100 nF (C1525), 10 nF (C15195), 4.7 kΩ (C25900), 10 kΩ (C25744).
