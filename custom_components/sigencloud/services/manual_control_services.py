import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers.debounce import Debouncer

from ..api import SigenCloudApi, SigenCloudApiError
from ..const import DOMAIN
from ..coordinator import SpikeLoadCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_MANUAL_CONTROL = "manual_control"
SERVICE_MANUAL_CONTROL_ALIAS = "manual-control"

_REFRESH_COOLDOWN_SECONDS = 5.0

_SCHEMA_MANUAL_CONTROL = vol.Schema(
    {
        vol.Required("enable"): cv.boolean,
        vol.Optional("mode"): vol.All(vol.Coerce(int), vol.In([0, 1, 2, 3])),
        vol.Optional("duration"): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Optional("power_limitation"): vol.Any("", vol.Coerce(float)),
    }
)


class ManualControlServices:
    def __init__(
        self,
        hass: HomeAssistant,
        api: SigenCloudApi,
        coordinator: SpikeLoadCoordinator | None = None,
    ) -> None:
        self._hass = hass
        self._api = api
        self._coordinator = coordinator
        self._refresh_debouncer: Debouncer | None = None
        if coordinator is not None:
            self._refresh_debouncer = Debouncer(
                hass,
                _LOGGER,
                cooldown=_REFRESH_COOLDOWN_SECONDS,
                immediate=False,
                function=coordinator.async_refresh,
            )

    async def _handle_manual_control(self, call: ServiceCall) -> dict:
        if call.data["enable"] and (
            "mode" not in call.data or "duration" not in call.data
        ):
            raise ValueError("mode and duration are required when enabling manual control")

        try:
            result = await self._api.manual_control(
                enable=call.data["enable"],
                mode=call.data.get("mode"),
                duration=call.data.get("duration"),
                power_limitation=call.data.get("power_limitation"),
            )
            _LOGGER.info("Manual control submitted successfully")
            await self._async_refresh_coordinator()
            if isinstance(result, dict):
                return {"success": result.get("data", True)}
            return {"success": bool(result)}
        except SigenCloudApiError as err:
            _LOGGER.error("Failed to submit manual control: %s", err)
            raise

    async def _async_refresh_coordinator(self) -> None:
        if self._refresh_debouncer is not None:
            await self._refresh_debouncer.async_call()

    def register(self) -> None:
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_MANUAL_CONTROL,
            self._handle_manual_control,
            schema=_SCHEMA_MANUAL_CONTROL,
            supports_response=SupportsResponse.OPTIONAL,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_MANUAL_CONTROL_ALIAS,
            self._handle_manual_control,
            schema=_SCHEMA_MANUAL_CONTROL,
            supports_response=SupportsResponse.OPTIONAL,
        )

    def unregister(self) -> None:
        if self._refresh_debouncer is not None:
            self._refresh_debouncer.async_shutdown()
        self._hass.services.async_remove(DOMAIN, SERVICE_MANUAL_CONTROL)
        self._hass.services.async_remove(DOMAIN, SERVICE_MANUAL_CONTROL_ALIAS)
