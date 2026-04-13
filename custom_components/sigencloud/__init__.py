import logging
from datetime import date

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .api import SigenCloudApi, SigenCloudApiError
from .const import CONF_STATION_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_SPIKE_LOAD = "add_spike_load"
SERVICE_GET_SPIKE_LOADS = "get_spike_loads"
SERVICE_REMOVE_SPIKE_LOAD = "remove_spike_load"

SERVICE_ADD_SPIKE_LOAD_SCHEMA = vol.Schema(
    {
        vol.Required("load_type"): vol.All(int, vol.Range(min=1)),
        vol.Required("start_time"): cv.string,
        vol.Optional("start_date"): cv.string,
        vol.Required("duration"): vol.All(int, vol.Range(min=1)),
        vol.Required("power"): vol.All(vol.Coerce(float), vol.Range(min=0)),
    }
)

SERVICE_GET_SPIKE_LOADS_SCHEMA = vol.Schema({})

SERVICE_REMOVE_SPIKE_LOAD_SCHEMA = vol.Schema(
    {
        vol.Required("event_id"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = SigenCloudApi(
        entry.data["username"],
        entry.data["password"],
        entry.data[CONF_STATION_ID],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    async def handle_add_spike_load(call: ServiceCall) -> None:
        start_date = call.data.get("start_date", date.today().isoformat())
        start_time = call.data["start_time"][:5]  # trim HH:MM:SS → HH:MM
        try:
            await api.add_spike_load(
                load_type=call.data["load_type"],
                start_time=start_time,
                start_date=start_date,
                duration=call.data["duration"],
                power=call.data["power"],
            )
            _LOGGER.info("Spike load submitted successfully")
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to submit spike load: %s", err)

    async def handle_get_spike_loads(call: ServiceCall) -> dict:
        try:
            items = await api.get_spike_loads() or []
            count = len(items)
            _LOGGER.info("Fetched %s spike load record(s)", count)
            return {"spikeLoads": items}
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to fetch spike loads: %s", err)
            raise

    async def handle_remove_spike_load(call: ServiceCall) -> None:
        try:
            await api.remove_spike_load(event_id=call.data["event_id"])
            _LOGGER.info("Spike load removed successfully (event_id=%s)", call.data["event_id"])
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to remove spike load: %s", err)
            raise

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SPIKE_LOAD,
        handle_add_spike_load,
        schema=SERVICE_ADD_SPIKE_LOAD_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SPIKE_LOADS,
        handle_get_spike_loads,
        schema=SERVICE_GET_SPIKE_LOADS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_SPIKE_LOAD,
        handle_remove_spike_load,
        schema=SERVICE_REMOVE_SPIKE_LOAD_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api: SigenCloudApi = hass.data[DOMAIN].pop(entry.entry_id)
    await api.close()
    hass.services.async_remove(DOMAIN, SERVICE_ADD_SPIKE_LOAD)
    hass.services.async_remove(DOMAIN, SERVICE_GET_SPIKE_LOADS)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_SPIKE_LOAD)
    return True
