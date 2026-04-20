import logging
from datetime import date

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_SPIKE_LOAD = "add_spike_load"
SERVICE_GET_SPIKE_LOADS = "get_spike_loads"
SERVICE_REMOVE_SPIKE_LOAD = "remove_spike_load"

_SCHEMA_ADD = vol.Schema(
    {
        vol.Required("load_type"): vol.All(int, vol.Range(min=1)),
        vol.Required("start_time"): cv.string,
        vol.Optional("start_date"): cv.string,
        vol.Required("duration"): vol.All(int, vol.Range(min=1)),
        vol.Required("power"): vol.All(vol.Coerce(float), vol.Range(min=0)),
    }
)

_SCHEMA_GET = vol.Schema({})

_SCHEMA_REMOVE = vol.Schema(
    {
        vol.Required("event_id"): cv.string,
    }
)


class SpikeLoadServices:
    def __init__(self, hass: HomeAssistant, api: SigenCloudApi) -> None:
        self._hass = hass
        self._api = api

    async def _handle_add(self, call: ServiceCall) -> None:
        start_date = call.data.get("start_date", date.today().isoformat())
        start_time = call.data["start_time"][:5]  # trim HH:MM:SS → HH:MM
        try:
            await self._api.add_spike_load(
                load_type=call.data["load_type"],
                start_time=start_time,
                start_date=start_date,
                duration=call.data["duration"],
                power=call.data["power"],
            )
            _LOGGER.info("Spike load submitted successfully")
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to submit spike load: %s", err)

    async def _handle_get(self, call: ServiceCall) -> dict:
        try:
            items = await self._api.get_spike_loads() or []
            _LOGGER.info("Fetched %s spike load record(s)", len(items))
            return {"spikeLoads": items}
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to fetch spike loads: %s", err)
            raise

    async def _handle_remove(self, call: ServiceCall) -> None:
        try:
            await self._api.remove_spike_load(event_id=call.data["event_id"])
            _LOGGER.info("Spike load removed successfully (event_id=%s)", call.data["event_id"])
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to remove spike load: %s", err)
            raise

    def register(self) -> None:
        self._hass.services.async_register(
            DOMAIN, SERVICE_ADD_SPIKE_LOAD, self._handle_add, schema=_SCHEMA_ADD
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_GET_SPIKE_LOADS,
            self._handle_get,
            schema=_SCHEMA_GET,
            supports_response=SupportsResponse.OPTIONAL,
        )
        self._hass.services.async_register(
            DOMAIN, SERVICE_REMOVE_SPIKE_LOAD, self._handle_remove, schema=_SCHEMA_REMOVE
        )

    def unregister(self) -> None:
        self._hass.services.async_remove(DOMAIN, SERVICE_ADD_SPIKE_LOAD)
        self._hass.services.async_remove(DOMAIN, SERVICE_GET_SPIKE_LOADS)
        self._hass.services.async_remove(DOMAIN, SERVICE_REMOVE_SPIKE_LOAD)
