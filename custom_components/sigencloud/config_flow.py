import logging

import voluptuous as vol
from homeassistant import config_entries

from .api import SigenCloudApi, SigenCloudApiError
from .const import CONF_STATION_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required(CONF_STATION_ID): vol.Coerce(int),
    }
)


class SigenCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api = SigenCloudApi(
                user_input["username"],
                user_input["password"],
                user_input[CONF_STATION_ID],
            )
            try:
                await api.login()
            except SigenCloudApiError as err:
                _LOGGER.error("SigenCloud login failed: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await api.close()

            if not errors:
                await self.async_set_unique_id(str(user_input[CONF_STATION_ID]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="SigenCloud", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
