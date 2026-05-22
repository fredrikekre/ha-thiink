from __future__ import annotations

import aiohttp
import voluptuous as vol

from .pythiink import ThiinkClient, ThiinkConnectionError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DOMAIN

CONF_BASE_URL = "base_url"

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
})


async def _detect_base_url(host: str, session: aiohttp.ClientSession) -> tuple[str, str]:
    """Try HTTPS then HTTP. Returns (base_url, device_id) or raises ThiinkConnectionError."""
    host = host.strip()
    # If the user already included a scheme, use it directly.
    if host.startswith(("http://", "https://")):
        candidates = [host]
    else:
        candidates = [f"https://{host}", f"http://{host}"]

    last_err: Exception | None = None
    for base_url in candidates:
        try:
            client = ThiinkClient(base_url, session)
            status = await client.get_status()
            return base_url, status.device_id
        except ThiinkConnectionError as err:
            last_err = err

    raise ThiinkConnectionError(f"Could not connect to {host}") from last_err


class ThiinkConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    base_url, device_id = await _detect_base_url(user_input[CONF_HOST], session)
            except ThiinkConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Thiink ({user_input[CONF_HOST]})",
                    data={CONF_BASE_URL: base_url},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
