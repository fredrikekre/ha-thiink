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

        # Usually one schedule entry is marked with `active: true` but not always is an
        # entry marked as such (for some reason) so instead we just pick whatever schedule
        # entry that matches the current time.
        now = datetime.now(timezone.utc)
        selected = None
        for entry in entries:
            if entry.start_at > now:
                break
            selected = entry

        # If no time-based entry found (impossible hopefully) we fail the update
        if selected is None:
            msg = "No schedule entry matches the current time"
            _LOGGER.debug(msg)
            raise UpdateFailed(msg)

        # If one entry _is_ marked active we check that it matches the one we selected.
        # Since we do updates right at the 15 minute marks the active entry haven't always
        # updated yet but we still use the entry that is intended to be used for the current
        # time.
        marked_active = next((e for e in entries if e.active), None)
        if marked_active is None:
            _LOGGER.debug("No schedule entry marked active")
        elif selected.start_at != marked_active.start_at:
                _LOGGER.debug(
                    "Selected schedule entry (start_at=%s) differs from active entry (start_at=%s)",
                    selected.start_at, marked_active.start_at,
                )

        return selected


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
