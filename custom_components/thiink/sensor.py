from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .pythiink import EmsData, StatusData

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
from homeassistant.core import HomeAssistant
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
        device_class=SensorDeviceClass.BATTERY,
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
        key="cabinet_temperature",
        translation_key="cabinet_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cabinet_temperature,
    ),
    ThiinkSensorEntityDescription(
        key="cabinet_humidity",
        translation_key="cabinet_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cabinet_humidity,
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

    async_add_entities(
        [ThiinkSensor(ems_coord, desc, entry) for desc in EMS_SENSORS]
        + [ThiinkSensor(status_coord, desc, entry) for desc in STATUS_SENSORS]
    )


class ThiinkSensor(CoordinatorEntity, SensorEntity):
    entity_description: ThiinkSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: ThiinkSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thiink",
            model="Connection Unit",
        )

    @property
    def native_value(self) -> Any:
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (AttributeError, TypeError):
            return None
