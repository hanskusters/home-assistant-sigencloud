import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from ..api import SigenCloudApi, SigenCloudApiError
from ..const import DOMAIN
from ..coordinator import ControlCoordinator
from ..helpers import limit_to_kw, resolve_limit

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_BATTERY_POWER_LIMIT = "set_battery_power_limit"
SERVICE_GET_BATTERY_POWER_LIMIT = "get_battery_power_limit"

_SCHEMA_SET = vol.Schema(
    {
        vol.Optional("max_charging_power"): vol.All(
            vol.Coerce(float), vol.Range(min=0)
        ),
        vol.Optional("max_discharging_power"): vol.All(
            vol.Coerce(float), vol.Range(min=0)
        ),
        vol.Optional("reset_charging", default=False): cv.boolean,
        vol.Optional("reset_discharging", default=False): cv.boolean,
    }
)

_SCHEMA_GET = vol.Schema({})


class BatteryLimitServices:
    def __init__(
        self,
        hass: HomeAssistant,
        api: SigenCloudApi,
        coordinator: ControlCoordinator | None = None,
    ) -> None:
        self._hass = hass
        self._api = api
        self._coordinator = coordinator

    async def _handle_set(self, call: ServiceCall) -> dict:
        charging = call.data.get("max_charging_power")
        discharging = call.data.get("max_discharging_power")
        reset_charging = call.data["reset_charging"]
        reset_discharging = call.data["reset_discharging"]

        if charging is None and discharging is None and not (
            reset_charging or reset_discharging
        ):
            raise ValueError(
                "Provide at least one of max_charging_power, max_discharging_power, "
                "reset_charging or reset_discharging"
            )

        try:
            current: dict = {}
            # Only fetch current limits when a field is omitted and must be kept
            if (charging is None and not reset_charging) or (
                discharging is None and not reset_discharging
            ):
                current = await self._api.get_battery_power_limit()

            result = await self._api.set_battery_power_limit(
                max_charging_power=resolve_limit(
                    charging,
                    reset_charging,
                    current.get("batteryMaxChargingPower"),
                    "max_charging_power",
                ),
                max_discharging_power=resolve_limit(
                    discharging,
                    reset_discharging,
                    current.get("batteryMaxDischargingPower"),
                    "max_discharging_power",
                ),
            )
            _LOGGER.info("Battery power limit submitted successfully")
            if self._coordinator is not None:
                await self._coordinator.async_request_refresh()
            if isinstance(result, dict):
                return {"success": result.get("data", True)}
            return {"success": bool(result)}
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to set battery power limit: %s", err)
            raise

    async def _handle_get(self, call: ServiceCall) -> dict:
        try:
            data = await self._api.get_battery_power_limit()
            return {
                "max_charging_power": limit_to_kw(data.get("batteryMaxChargingPower")),
                "max_discharging_power": limit_to_kw(
                    data.get("batteryMaxDischargingPower")
                ),
            }
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to fetch battery power limit: %s", err)
            raise

    def register(self) -> None:
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_SET_BATTERY_POWER_LIMIT,
            self._handle_set,
            schema=_SCHEMA_SET,
            supports_response=SupportsResponse.OPTIONAL,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_GET_BATTERY_POWER_LIMIT,
            self._handle_get,
            schema=_SCHEMA_GET,
            supports_response=SupportsResponse.OPTIONAL,
        )

    def unregister(self) -> None:
        self._hass.services.async_remove(DOMAIN, SERVICE_SET_BATTERY_POWER_LIMIT)
        self._hass.services.async_remove(DOMAIN, SERVICE_GET_BATTERY_POWER_LIMIT)
