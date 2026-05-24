# ha-thiink

Unofficial Home Assistant integration for the [Thiink](https://thiink.io) Control Unit.

> **Disclaimer:** This project is not affiliated with, endorsed by, or connected to Thiink
> in any way. It is an independent integration that uses the device's undocumented local
> HTTP API.

## Features

- Polls the CU's local HTTP API — no cloud dependency
- Sensors covering grid, battery, PV, load, and device environment
- Per-phase grid measurements (voltage, current, power) for three-phase installations
- Grid energy import/export counters compatible with the HA Energy Dashboard
- EMS schedule sensors reflecting the optimizer's currently active slot
- Two polling intervals: EMS data every 10 s, device status and schedule every 60 s

## Installation

1. Copy `custom_components/thiink/` into your Home Assistant config's `custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **Thiink**.
4. Enter the hostname or IP address of your Thiink Control Unit.

## Sensors

| Entity | Unit | Notes |
|--------|------|-------|
| Grid Power | W | Negative = export |
| Grid L1/L2/L3 Power | W | |
| Grid L1/L2/L3 Voltage | V | |
| Grid L1/L2/L3 Current | A | |
| Grid Energy Import | kWh | Cumulative |
| Grid Energy Export | kWh | Cumulative |
| PV Power | W | From inverter via Modbus |
| Battery Power | W | |
| Battery State of Charge | % | |
| Battery Voltage | V | |
| Battery Capacity | kWh | |
| Load Power | W | |
| Inverter Temperature | °C | |
| Battery Temperature | °C | |
| Device Internal Temperature | °C | Internal CU sensor |
| Device Internal Humidity | % | Internal CU sensor |
| Firmware Version | | |
| Ethernet Connected | | Binary sensor |

### Schedule sensors (active EMS slot)

| Entity | Unit | Notes |
|--------|------|-------|
| Schedule Mode | | `forced` or `balancing` |
| Schedule Dispatch | W | Target battery output (forced mode); positive = discharge, negative = charge |
| Schedule Charge Trigger | W | Grid export threshold to start charging (balancing mode) |
| Schedule Discharge Trigger | W | Grid import threshold to start discharging (balancing mode) |
| Schedule Max Charge | W | Maximum battery charge rate |
| Schedule Max Discharge | W | Maximum battery discharge rate |
| Schedule Max Export | W | Grid connection export cap |
| Schedule Max Import | W | Grid connection import cap |
| Schedule Min SoC | % | Minimum allowed state of charge |
| Schedule Max SoC | % | Maximum allowed state of charge |
| Schedule Hysteresis | W | Trigger deadband to prevent rapid switching |

## Requirements

- Home Assistant 2024.1 or later
- Thiink Control Unit on your local network (reachable by HTTP)
- No cloud account or internet access required for the integration

## Structure

```
custom_components/thiink/
├── pythiink/       # Pure Python API client (no HA dependency)
└── ...             # HA integration code
```

`pythiink/` is kept as a self-contained library with no Home Assistant dependencies so it can be published separately in the future.

## License

MIT License — see [LICENSE](LICENSE).
