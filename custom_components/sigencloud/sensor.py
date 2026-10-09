import logging

from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import (
    ControlCoordinator,
    SpikeLoadCoordinator,
    manual_control_end_time,
)
from .entity import SigenCloudEntity

_LOGGER = logging.getLogger(__name__)

# Human-readable labels for the loadType field returned by the API (0-based).
LOAD_TYPE_LABELS = {
    0: "Cloth Dryer",
    1: "Air Conditioner",
    2: "Dish Washer",
    3: "Washing Machine",
    4: "Car Charging",
    5: "Coffee Machine",
    6: "Floor Heating",
    7: "Fridge",
    8: "Heat Pump",
    9: "Heating And Cooling",
    10: "Hot Water",
    11: "Lights",
    12: "Microwave",
    13: "Oven",
    14: "Pool Pump",
    15: "Server Rack",
    16: "Thermostat",
    17: "Towel Rails",
    18: "TV",
    19: "Wine Cabinet",
    20: "Heat Pump",  # appears twice in the source list (also index 8)
    21: "Water Dispenser",
    22: "Medical Equipment",
    23: "Plug Socket",
    24: "Dehumidifier",
    25: "EVAC",
    26: "EVDC",
    27: "Other",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SpikeLoadCoordinator = entry_data["coordinator"]
    control_coordinator: ControlCoordinator = entry_data["control_coordinator"]
    async_add_entities(
        [
            SpikeLoadsSensor(coordinator, entry),
            ManualControlEndTimeSensor(control_coordinator, entry),
        ]
    )


class SpikeLoadsSensor(SigenCloudEntity, SensorEntity):
    """Sensor whose state is the number of spike loads, with the list in attributes."""

    _attr_name = "Spike loads"
    _attr_icon = "mdi:lightning-bolt"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: SpikeLoadCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "spike_loads")
        # Keep the explicit name so the existing entity_id is unchanged
        self._attr_translation_key = None
        self._update_from_coordinator()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_from_coordinator()
        super()._handle_coordinator_update()

    def _update_from_coordinator(self) -> None:
        records = self.coordinator.data or []
        self._attr_native_value = len(records)
        self._attr_extra_state_attributes = {
            "spike_loads": [
                {
                    "event_id": item.get("eventId"),
                    "load_type": item.get("loadType"),
                    "load_type_label": LOAD_TYPE_LABELS.get(
                        item.get("loadType"), "Unknown"
                    ),
                    "start_date": item.get("startDate"),
                    "start_time": item.get("startTime"),
                    "duration": item.get("duration"),
                    "power": item.get("power"),
                }
                for item in records
            ]
        }


class ManualControlEndTimeSensor(SigenCloudEntity, SensorEntity):
    """Timestamp at which the active manual control ends (unknown when off)."""

    _attr_icon = "mdi:timer-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: ControlCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "manual_control_end_time")

    @property
    def native_value(self) -> datetime | None:
        end_time = manual_control_end_time(self.coordinator.data)
        if end_time is None:
            return None
        return datetime.fromtimestamp(end_time, tz=timezone.utc)
