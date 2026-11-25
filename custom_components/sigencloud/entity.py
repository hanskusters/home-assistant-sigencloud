from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_STATION_ID, DOMAIN

DEFAULT_MANUAL_CONTROL_DURATION = 60
DEFAULT_MANUAL_CONTROL_POWER_LIMIT = 0.0


@dataclass
class ManualControlSettings:
    """Local settings used when the manual control select enables a mode."""

    duration: int = DEFAULT_MANUAL_CONTROL_DURATION
    # kW; 0 means no power limitation
    power_limit: float = DEFAULT_MANUAL_CONTROL_POWER_LIMIT


def device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, str(entry.data[CONF_STATION_ID]))},
        name="SigenCloud",
        manufacturer="Sigenergy",
    )


class SigenCloudEntity(CoordinatorEntity[DataUpdateCoordinator]):  # type: ignore[misc]
    """Base entity attached to the SigenCloud station device."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: DataUpdateCoordinator, entry: ConfigEntry, key: str
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = device_info(entry)
