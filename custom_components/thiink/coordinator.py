import logging
from datetime import timedelta

from .pythiink import ThiinkClient, ThiinkConnectionError, EmsData, StatusData

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
            raise UpdateFailed(err) from err


class ThiinkStatusCoordinator(DataUpdateCoordinator[StatusData]):
    """Polls device status every 60 seconds."""

    def __init__(self, hass: HomeAssistant, client: ThiinkClient) -> None:
        super().__init__(hass, _LOGGER, name="Thiink Status", update_interval=timedelta(seconds=60))
        self._client = client

    async def _async_update_data(self) -> StatusData:
        try:
            return await self._client.get_status()
        except ThiinkConnectionError as err:
            raise UpdateFailed(err) from err
