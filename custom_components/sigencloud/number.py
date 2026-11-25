import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN
from .coordinator import ControlCoordinator
from .entity import ManualControlSettings, SigenCloudEntity, device_info
from .helpers import limit_to_kw, resolve_limit

_LOGGER = logging.getLogger(__name__)

CHARGING_FIELD = "batteryMaxChargingPower"
DISCHARGING_FIELD = "batteryMaxDischargingPower"
# Upper bound for the UI only; the system enforces its own hardware maximum.
_MAX_POWER_KW = 100.0


async def async_set_battery_limit(
    api: SigenCloudApi,
    coordinator: ControlCoordinator,
    field: str,
    value: float | None = None,
    reset: bool = False,
) -> None:
    """Set or reset one battery limit field, keeping the other at its current value."""
    try:
        current = (coordinator.data or {}).get("battery_limit") or {}
        if not current:
            current = await api.get_battery_power_limit()
        values = {
            name: resolve_limit(
                value if name == field else None,
                reset and name == field,
                current.get(name),
                name,
            )
            for name in (CHARGING_FIELD, DISCHARGING_FIELD)
        }
        await api.set_battery_power_limit(
            max_charging_power=values[CHARGING_FIELD],
            max_discharging_power=values[DISCHARGING_FIELD],
        )
    except SigenCloudApiError as err:
        raise HomeAssistantError(f"Failed to set battery power limit: {err}") from err
    _LOGGER.info("Battery power limit %s updated", field)
    await coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api: SigenCloudApi = entry_data["api"]
    coordinator: ControlCoordinator = entry_data["control_coordinator"]
    settings: ManualControlSettings = entry_data["manual_control_settings"]
    async_add_entities(
        [
            BatteryLimitNumber(
                coordinator, entry, api, "battery_max_charging_power", CHARGING_FIELD
            ),
            BatteryLimitNumber(
                coordinator,
                entry,
                api,
                "battery_max_discharging_power",
                DISCHARGING_FIELD,
            ),
            ManualControlDurationNumber(entry, settings),
            ManualControlPowerLimitNumber(entry, settings),
        ]
    )


class BatteryLimitNumber(SigenCloudEntity, NumberEntity):
    """Battery max (dis)charging power; unknown when it depends on the system."""

    _attr_device_class = NumberDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_native_min_value = 0.0
    _attr_native_max_value = _MAX_POWER_KW
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX

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

    @property
    def _raw(self) -> str | None:
        return ((self.coordinator.data or {}).get("battery_limit") or {}).get(
            self._field
        )

    @property
    def native_value(self) -> float | None:
        return limit_to_kw(self._raw)

    @property
    def extra_state_attributes(self) -> dict:
        return {"system_default": self._raw is not None and self.native_value is None}

    async def async_set_native_value(self, value: float) -> None:
        await async_set_battery_limit(self._api, self.coordinator, self._field, value)


class _ManualControlSettingNumber(RestoreNumber):
    """Locally stored setting used by the manual control select."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_should_poll = False

    def __init__(
        self, entry: ConfigEntry, settings: ManualControlSettings, key: str
    ) -> None:
        self._settings = settings
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = device_info(entry)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._store(last.native_value)

    async def async_set_native_value(self, value: float) -> None:
        self._store(value)
        self.async_write_ha_state()

    def _store(self, value: float) -> None:
        raise NotImplementedError


class ManualControlDurationNumber(_ManualControlSettingNumber):
    _attr_icon = "mdi:timer-cog-outline"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = 1
    _attr_native_max_value = 1440
    _attr_native_step = 1

    def __init__(self, entry: ConfigEntry, settings: ManualControlSettings) -> None:
        super().__init__(entry, settings, "manual_control_duration")

    @property
    def native_value(self) -> float:
        return self._settings.duration

    def _store(self, value: float) -> None:
        self._settings.duration = int(value)


class ManualControlPowerLimitNumber(_ManualControlSettingNumber):
    _attr_device_class = NumberDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_native_min_value = 0.0
    _attr_native_max_value = _MAX_POWER_KW
    _attr_native_step = 0.1

    def __init__(self, entry: ConfigEntry, settings: ManualControlSettings) -> None:
        super().__init__(entry, settings, "manual_control_power_limit")

    @property
    def native_value(self) -> float:
        return self._settings.power_limit

    def _store(self, value: float) -> None:
        self._settings.power_limit = float(value)
