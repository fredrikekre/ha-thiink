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
| Grid power | W | Negative = export |
| Grid L1/L2/L3 power | W | |
| Grid L1/L2/L3 voltage | V | |
| Grid L1/L2/L3 current | A | |
| Grid energy import | kWh | Cumulative |
| Grid energy export | kWh | Cumulative |
| PV power | W | |
| Battery power | W | |
| Battery state of charge | % | |
| Battery voltage | V | |
| Battery capacity | kWh | |
| Load power | W | |
| Inverter temperature | °C | |
| Battery temperature | °C | |
| Device internal temperature | °C | Internal CU sensor |
| Device internal humidity | % | Internal CU sensor |
| Firmware version | | |
| Ethernet connected | | Binary sensor |

### Schedule sensors (active EMS slot)

| Entity | Unit | Notes |
|--------|------|-------|
| Schedule mode | | `forced` or `balancing` |
| Schedule battery dispatch power | W | Target battery output in forced mode; positive = discharge, negative = charge |
| Schedule charge trigger | W | Grid export threshold to start charging (balancing mode) |
| Schedule discharge trigger | W | Grid import threshold to start discharging (balancing mode) |
| Schedule max charge | W | Maximum battery charge rate |
| Schedule max discharge | W | Maximum battery discharge rate |
| Schedule max export | W | Grid connection export cap |
| Schedule max import | W | Grid connection import cap |
| Schedule min SoC | % | Minimum allowed state of charge |
| Schedule max SoC | % | Maximum allowed state of charge |
| Schedule hysteresis | W | Trigger deadband to prevent rapid switching |

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
