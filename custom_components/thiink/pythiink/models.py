from dataclasses import dataclass


@dataclass
class PhaseValues:
    l1: float
    l2: float
    l3: float


@dataclass
class GridDetails:
    voltage: PhaseValues
    power: PhaseValues
    current: PhaseValues
    energy_import: float  # kWh, cumulative
    energy_export: float  # kWh, cumulative


@dataclass
class BatteryDetails:
    capacity: float  # kWh
    voltage: float   # V


@dataclass
class EmsData:
    """Data from GET /data?state=ems."""

    grid_power: float           # W, negative = export
    pv_power: float             # W
    battery_power: float        # W
    load_power: float           # W
    soc: float                  # %
    grid: GridDetails
    battery: BatteryDetails
    inverter_temperature: float  # °C
    battery_temperature: float   # °C


@dataclass
class StatusData:
    """Data from GET /data."""

    cabinet_temperature: float  # °C
    cabinet_humidity: float     # %
    fw_version: str
    hw_version: str
    device_id: str
