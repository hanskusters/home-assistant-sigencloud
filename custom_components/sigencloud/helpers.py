from .const import BATTERY_LIMIT_SYSTEM_DEFAULT


def limit_to_kw(value: str | None) -> float | None:
    """Convert an API limit string to kW; None means 'depends on system'."""
    if value is None or value == BATTERY_LIMIT_SYSTEM_DEFAULT:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def resolve_limit(
    value: float | None, reset: bool, current: str | None, name: str
) -> str:
    """Return the API string for a limit field: new value, reset, or keep current."""
    if value is not None and reset:
        raise ValueError(f"Cannot set {name} and reset it at the same time")
    if reset:
        return BATTERY_LIMIT_SYSTEM_DEFAULT
    if value is not None:
        return f"{value:.3f}"
    return current if current is not None else BATTERY_LIMIT_SYSTEM_DEFAULT
