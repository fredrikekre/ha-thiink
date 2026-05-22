from __future__ import annotations

import aiohttp
import voluptuous as vol

from .pythiink import ThiinkClient, ThiinkConnectionError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
})


class ThiinkConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                async with aiohttp.ClientSession() as session:
                    client = ThiinkClient(host, session)
                    status = await client.get_status()
            except ThiinkConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(status.device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Thiink {host}", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
