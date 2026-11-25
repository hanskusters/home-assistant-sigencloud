import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN, MANUAL_CONTROL_MODES
from .coordinator import ControlCoordinator, manual_control_end_time
from .entity import ManualControlSettings, SigenCloudEntity

_LOGGER = logging.getLogger(__name__)

OPTION_OFF = "off"
_MODE_BY_OPTION = {option: mode for mode, option in MANUAL_CONTROL_MODES.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ManualControlSelect(
                entry_data["control_coordinator"],
                entry,
                entry_data["api"],
                entry_data["manual_control_settings"],
            )
        ]
    )


class ManualControlSelect(SigenCloudEntity, SelectEntity):
    """Select to switch manual control off or into one of its modes."""

    _attr_icon = "mdi:battery-sync"
    _attr_options = [OPTION_OFF, *MANUAL_CONTROL_MODES.values()]

    def __init__(
        self,
        coordinator: ControlCoordinator,
        entry: ConfigEntry,
        api: SigenCloudApi,
        settings: ManualControlSettings,
    ) -> None:
        super().__init__(coordinator, entry, "manual_control")
        self._api = api
        self._settings = settings

    @property
    def _manual(self) -> dict:
        return (self.coordinator.data or {}).get("manual_control") or {}

    @property
    def current_option(self) -> str | None:
        manual = self._manual
        if not manual:
            return None
        if not manual.get("enable"):
            return OPTION_OFF
        try:
            return MANUAL_CONTROL_MODES.get(int(manual.get("mode")))
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict:
        return {"end_time": manual_control_end_time(self.coordinator.data)}

    async def async_select_option(self, option: str) -> None:
        try:
            if option == OPTION_OFF:
                await self._api.manual_control(enable=False)
            else:
                power_limit = self._settings.power_limit
                await self._api.manual_control(
                    enable=True,
                    mode=_MODE_BY_OPTION[option],
                    duration=self._settings.duration,
                    power_limitation=power_limit if power_limit > 0 else None,
                )
        except SigenCloudApiError as err:
            raise HomeAssistantError(f"Failed to set manual control: {err}") from err
        _LOGGER.info("Manual control set to %s", option)
        await self.coordinator.async_request_refresh()
