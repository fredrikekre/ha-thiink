import logging
from datetime import datetime, timedelta, timezone

from .pythiink import ThiinkClient, ThiinkConnectionError, EmsData, ScheduleEntry, StatusData

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class ThiinkEmsCoordinator(DataUpdateCoordinator[EmsData]):
    """Polls EMS data every 10 seconds."""

    def __init__(self, hass: HomeAssistant, client: ThiinkClient) -> None:
        super().__init__(hass, _LOGGER, name="Thiink EMS", update_interval=timedelta(seconds=10))
        self._client = client

    async def _async_update_data(self) -> EmsData:
        try:
            return await self._client.get_ems()
        except ThiinkConnectionError as err:
            _LOGGER.warning("EMS update failed: %s", err)
            raise UpdateFailed(err) from err

class ThiinkScheduleCoordinator(DataUpdateCoordinator[ScheduleEntry]):
    """Polls schedule data every 60 seconds, resolving the current active entry."""

    def __init__(self, hass: HomeAssistant, client: ThiinkClient) -> None:
        super().__init__(hass, _LOGGER, name="Thiink Schedule", update_interval=timedelta(seconds=60))
        self._client = client

    async def _async_update_data(self) -> ScheduleEntry:
        try:
            entries = await self._client.get_schedule()
        except ThiinkConnectionError as err:
            _LOGGER.warning("Schedule update failed: %s", err)
            raise UpdateFailed(err) from err

        # Return the active entry (if one is marked as such)
        active = next((e for e in entries if e.active), None)
        if active is not None:
            return active

        # Time-based fallback: pick the entry with highest start_at <= now
        now = datetime.now(timezone.utc)
        fallback = None
        for entry in entries:
            if entry.start_at > now:
                break
            fallback = entry
        if fallback is not None:
            _LOGGER.debug("No active schedule entry, using time-based fallback with start_at=%s", fallback.start_at)
            return fallback

        # Final fallback: use current data if it exist
        if self.data is not None:
            _LOGGER.debug("No eligible schedule entry found, retaining last known values")
            return self.data

        raise UpdateFailed("No active or eligible schedule entry and no previous data available")


class ThiinkStatusCoordinator(DataUpdateCoordinator[StatusData]):
    """Polls device status every 60 seconds."""

    def __init__(self, hass: HomeAssistant, client: ThiinkClient) -> None:
        super().__init__(hass, _LOGGER, name="Thiink Status", update_interval=timedelta(seconds=60))
        self._client = client

    async def _async_update_data(self) -> StatusData:
        try:
            return await self._client.get_status()
        except ThiinkConnectionError as err:
            _LOGGER.warning("Status update failed: %s", err)
            raise UpdateFailed(err) from err
