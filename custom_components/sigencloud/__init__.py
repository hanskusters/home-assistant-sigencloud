import logging
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .api import SigenCloudApi, SigenCloudApiError
from .const import CONF_STATION_ID, DOMAIN
from .coordinator import SpikeLoadCoordinator
from .spike_load_services import SpikeLoadServices

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = SigenCloudApi(
        entry.data["username"],
        entry.data["password"],
        entry.data[CONF_STATION_ID],
    )

    await api.login()

    _cancel_refresh: list[Callable | None] = [None]

    async def _refresh_token(_now=None) -> None:
        try:
            await api.login()
            _LOGGER.debug("Background token refresh successful")
        except SigenCloudApiError as err:
            _LOGGER.warning("Background token refresh failed: %s", err)
        finally:
            _schedule_next_refresh()

    def _schedule_next_refresh() -> None:
        delay = api.refresh_in
        if delay is not None and delay > 0:
            _cancel_refresh[0] = async_call_later(hass, delay, _refresh_token)
            _LOGGER.debug("Next token refresh scheduled in %.0f seconds", delay)

    _schedule_next_refresh()

    coordinator = SpikeLoadCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    services = SpikeLoadServices(hass, api, coordinator)
    services.register()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "cancel_refresh": _cancel_refresh,
        "coordinator": coordinator,
        "services": services,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    entry_data = hass.data[DOMAIN].pop(entry.entry_id)
    api: SigenCloudApi = entry_data["api"]
    cancel_refresh = entry_data["cancel_refresh"]
    if cancel_refresh[0] is not None:
        cancel_refresh[0]()
    await api.close()
    entry_data["services"].unregister()
    return True
