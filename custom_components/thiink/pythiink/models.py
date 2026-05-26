from dataclasses import dataclass
from datetime import datetime


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
    eth_status: str             # "connected" / "disconnected"


@dataclass
class ScheduleEntry:
    """A single EMS schedule slot from GET /data?key=schedule."""

    mode: str           # "forced" or "balancing"
    dispatch: int       # W, positive = discharge, negative = charge (forced mode)
    trig_charge: int    # W, grid export threshold to start charging (balancing mode)
    trig_discharge: int # W, grid import threshold to start discharging (balancing mode)
    max_charge: int     # W
    max_discharge: int  # W
    max_export: int     # W
    max_import: int     # W
    min_soc: int        # %
    max_soc: int        # %
    hysteresis: int     # W
    start_at: datetime.datetime # UTC
    active: bool        # True if this entry is currently active
