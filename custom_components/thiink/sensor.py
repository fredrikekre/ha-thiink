from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .pythiink import EmsData, ScheduleEntry, StatusData

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class ThiinkSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[Any], Any]


EMS_SENSORS: tuple[ThiinkSensorEntityDescription, ...] = (
    # --- Grid ---
    ThiinkSensorEntityDescription(
        key="grid_power",
        translation_key="grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid_power,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l1_power",
        translation_key="grid_l1_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.power.l1,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l2_power",
        translation_key="grid_l2_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.power.l2,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l3_power",
        translation_key="grid_l3_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.power.l3,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l1_voltage",
        translation_key="grid_l1_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.voltage.l1,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l2_voltage",
        translation_key="grid_l2_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.voltage.l2,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l3_voltage",
        translation_key="grid_l3_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.voltage.l3,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l1_current",
        translation_key="grid_l1_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.current.l1,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l2_current",
        translation_key="grid_l2_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.current.l2,
    ),
    ThiinkSensorEntityDescription(
        key="grid_l3_current",
        translation_key="grid_l3_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.grid.current.l3,
    ),
    ThiinkSensorEntityDescription(
        key="grid_energy_import",
        translation_key="grid_energy_import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.grid.energy_import,
    ),
    ThiinkSensorEntityDescription(
        key="grid_energy_export",
        translation_key="grid_energy_export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.grid.energy_export,
    ),
    # --- PV ---
    ThiinkSensorEntityDescription(
        key="pv_power",
        translation_key="pv_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.pv_power,
    ),
    # --- Battery ---
    ThiinkSensorEntityDescription(
        key="battery_power",
        translation_key="battery_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery_power,
    ),
    ThiinkSensorEntityDescription(
        key="battery_soc",
        translation_key="battery_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.soc,
    ),
    ThiinkSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery.voltage,
    ),
    ThiinkSensorEntityDescription(
        key="battery_capacity",
        translation_key="battery_capacity",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery.capacity,
    ),
    # --- Load ---
    ThiinkSensorEntityDescription(
        key="load_power",
        translation_key="load_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.load_power,
    ),
    # --- Temperatures ---
    ThiinkSensorEntityDescription(
        key="inverter_temperature",
        translation_key="inverter_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.inverter_temperature,
    ),
    ThiinkSensorEntityDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery_temperature,
    ),
)

STATUS_SENSORS: tuple[ThiinkSensorEntityDescription, ...] = (
    ThiinkSensorEntityDescription(
        key="device_temperature",
        translation_key="device_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cabinet_temperature,
    ),
    ThiinkSensorEntityDescription(
        key="device_humidity",
        translation_key="device_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cabinet_humidity,
    ),
    ThiinkSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        value_fn=lambda d: d.fw_version,
    ),
)


SCHEDULE_SENSORS: tuple[ThiinkSensorEntityDescription, ...] = (
    ThiinkSensorEntityDescription(
        key="schedule_mode",
        translation_key="schedule_mode",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        value_fn=lambda d: d.mode,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_dispatch",
        translation_key="schedule_dispatch",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.dispatch,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_trig_charge",
        translation_key="schedule_trig_charge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.trig_charge,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_trig_discharge",
        translation_key="schedule_trig_discharge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.trig_discharge,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_max_charge",
        translation_key="schedule_max_charge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.max_charge,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_max_discharge",
        translation_key="schedule_max_discharge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.max_discharge,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_max_export",
        translation_key="schedule_max_export",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.max_export,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_max_import",
        translation_key="schedule_max_import",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.max_import,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_min_soc",
        translation_key="schedule_min_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.min_soc,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_max_soc",
        translation_key="schedule_max_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.max_soc,
    ),
    ThiinkSensorEntityDescription(
        key="schedule_hysteresis",
        translation_key="schedule_hysteresis",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.hysteresis,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    ems_coord: DataUpdateCoordinator[EmsData] = coordinators["ems"]
    status_coord: DataUpdateCoordinator[StatusData] = coordinators["status"]
    schedule_coord: DataUpdateCoordinator[ScheduleEntry] = coordinators["schedule"]
    status = status_coord.data

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        connections={(dr.CONNECTION_NETWORK_MAC, status.device_id)} if status and status.device_id else set(),
        name=entry.title,
        manufacturer="Thiink",
        model="Thiink Control Unit",
        hw_version=status.hw_version if status else None,
        sw_version=status.fw_version if status else None,
    )

    async_add_entities(
        [ThiinkSensor(ems_coord, desc, device_info) for desc in EMS_SENSORS]
        + [ThiinkSensor(status_coord, desc, device_info) for desc in STATUS_SENSORS]
        + [ThiinkSensor(schedule_coord, desc, device_info) for desc in SCHEDULE_SENSORS]
    )

    device_registry = dr.async_get(hass)

    @callback
    def _update_device_info(_now: Any = None) -> None:
        data = status_coord.data
        if not data:
            return
        device_entry = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
        if device_entry:
            device_registry.async_update_device(
                device_entry.id,
                sw_version=data.fw_version,
                hw_version=data.hw_version,
            )

    entry.async_on_unload(status_coord.async_add_listener(_update_device_info))


class ThiinkSensor(CoordinatorEntity, SensorEntity):
    entity_description: ThiinkSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: ThiinkSensorEntityDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{next(iter(device_info['identifiers']))[1]}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> Any:
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (AttributeError, TypeError):
            return None
