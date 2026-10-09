import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN
from .coordinator import ControlCoordinator, SpikeLoadCoordinator
from .entity import SigenCloudEntity
from .number import CHARGING_FIELD, DISCHARGING_FIELD, async_set_battery_limit

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api: SigenCloudApi = entry_data["api"]
    coordinator: ControlCoordinator = entry_data["control_coordinator"]
    async_add_entities(
        [
            ResetBatteryLimitButton(
                coordinator, entry, api, "reset_charging_limit", CHARGING_FIELD
            ),
            ResetBatteryLimitButton(
                coordinator, entry, api, "reset_discharging_limit", DISCHARGING_FIELD
            ),
            ClearSpikeLoadsButton(entry_data["coordinator"], entry, api),
        ]
    )


class ResetBatteryLimitButton(SigenCloudEntity, ButtonEntity):
    """Reset a battery power limit to 'depends on system'."""

    _attr_icon = "mdi:restore"

    def __init__(
        self,
        coordinator: ControlCoordinator,
        entry: ConfigEntry,
        api: SigenCloudApi,
        key: str,
        field: str,
    ) -> None:
        super().__init__(coordinator, entry, key)
        self._api = api
        self._field = field

    async def async_press(self) -> None:
        await async_set_battery_limit(
            self._api, self.coordinator, self._field, reset=True
        )


class ClearSpikeLoadsButton(SigenCloudEntity, ButtonEntity):
    """Remove all spike load records of the station."""

    _attr_icon = "mdi:delete-sweep"

    def __init__(
        self, coordinator: SpikeLoadCoordinator, entry: ConfigEntry, api: SigenCloudApi
    ) -> None:
        super().__init__(coordinator, entry, "clear_spike_loads")
        self._api = api

    async def async_press(self) -> None:
        try:
            # Fetch fresh: the coordinator data may be up to 15 minutes old
            records = await self._api.get_spike_loads() or []
            for record in records:
                event_id = record.get("eventId")
                if event_id is not None:
                    await self._api.remove_spike_load(event_id=str(event_id))
        except SigenCloudApiError as err:
            raise HomeAssistantError(f"Failed to clear spike loads: {err}") from err
        finally:
            await self.coordinator.async_request_refresh()
        _LOGGER.info("Cleared %s spike load record(s)", len(records))
