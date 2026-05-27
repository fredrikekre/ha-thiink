from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from .pythiink import ThiinkClient
from .config_flow import CONF_BASE_URL

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time

from .const import DOMAIN
from .coordinator import ThiinkEmsCoordinator, ThiinkScheduleCoordinator, ThiinkStatusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = ThiinkClient(entry.data[CONF_BASE_URL], session)

    ems = ThiinkEmsCoordinator(hass, client)
    status = ThiinkStatusCoordinator(hass, client)
    schedule = ThiinkScheduleCoordinator(hass, client)

    await ems.async_config_entry_first_refresh()
    await status.async_config_entry_first_refresh()
    await schedule.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"ems": ems, "status": status, "schedule": schedule}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Schedule exact quarter-hour boundary refreshes for the schedule coordinator.
    # This ensures entities are updated exactly at :00/:15/:30/:45.
    unsub_holder: dict[str, callable] = {"unsub": None}

    def next_quarter() -> datetime:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        future = now + timedelta(minutes=15)
        # Truncate to the previous multiple of 15
        minute = (future.minute // 15) * 15
        next_dt = future.replace(minute=minute, second=0, microsecond=0)
        return next_dt

    async def force_update_at_quarter_boundary(now: datetime) -> None:
        try:
            await schedule.async_request_refresh()
        except Exception:
            _LOGGER.exception("Failed to update schedule at 15-minute boundary")
        # Re-schedule the next exact boundary
        unsub_holder["unsub"] = async_track_point_in_utc_time(hass, force_update_at_quarter_boundary, next_quarter())

    # Start the repeating point-in-time scheduler
    unsub_holder["unsub"] = async_track_point_in_utc_time(hass, force_update_at_quarter_boundary, next_quarter())

    # Ensure the scheduled callback is removed on unload
    entry.async_on_unload(lambda: unsub_holder["unsub"] and unsub_holder["unsub"]())

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
