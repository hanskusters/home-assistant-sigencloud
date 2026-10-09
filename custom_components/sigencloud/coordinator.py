import logging
import time
from datetime import timedelta
from typing import Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SigenCloudApi, SigenCloudApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=15)
CONTROL_UPDATE_INTERVAL = timedelta(minutes=5)
# Extra delay after the manual control end time before re-fetching, so the
# cloud has had time to switch manual control off.
_END_TIME_REFRESH_MARGIN_SECONDS = 10


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


def manual_control_end_time(data: dict | None) -> float | None:
    """Return the manual control end time as epoch seconds, or None when disabled."""
    manual = (data or {}).get("manual_control") or {}
    if not manual.get("enable"):
        return None
    try:
        return float(manual.get("endTime"))
    except (TypeError, ValueError):
        return None


class ControlCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that fetches manual control state and battery power limits."""

    def __init__(self, hass: HomeAssistant, api: SigenCloudApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_control",
            update_interval=CONTROL_UPDATE_INTERVAL,
        )
        self._api = api
        self._cancel_end_refresh: Callable | None = None

    async def _async_update_data(self) -> dict:
        try:
            data = {
                "manual_control": await self._api.get_manual_control(),
                "battery_limit": await self._api.get_battery_power_limit(),
            }
        except SigenCloudApiError as err:
            raise UpdateFailed(f"Failed to fetch control state: {err}") from err
        self._schedule_end_refresh(data)
        return data

    @callback
    def _schedule_end_refresh(self, data: dict) -> None:
        """Refresh right after manual control ends so entities flip back to off."""
        self.cancel_end_refresh()
        end_time = manual_control_end_time(data)
        if end_time is None:
            return
        delay = end_time - time.time() + _END_TIME_REFRESH_MARGIN_SECONDS
        if delay <= 0 or delay > CONTROL_UPDATE_INTERVAL.total_seconds():
            # Already passed, or the regular poll will get there first
            return
        self._cancel_end_refresh = async_call_later(
            self.hass, delay, self._handle_end_refresh
        )

    async def _handle_end_refresh(self, _now=None) -> None:
        self._cancel_end_refresh = None
        await self.async_request_refresh()

    @callback
    def cancel_end_refresh(self) -> None:
        if self._cancel_end_refresh is not None:
            self._cancel_end_refresh()
            self._cancel_end_refresh = None
