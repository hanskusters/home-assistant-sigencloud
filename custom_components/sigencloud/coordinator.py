import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=15)


class SpikeLoadCoordinator(DataUpdateCoordinator[list]):
    """Coordinator that periodically fetches the station's spike load records."""

    def __init__(self, hass: HomeAssistant, api: SigenCloudApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_spike_loads",
            update_interval=UPDATE_INTERVAL,
        )
        self._api = api

    async def _async_update_data(self) -> list:
        try:
            return await self._api.get_spike_loads() or []
        except SigenCloudApiError as err:
            raise UpdateFailed(f"Failed to fetch spike loads: {err}") from err
