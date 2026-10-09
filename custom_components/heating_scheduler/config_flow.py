"""Configure Heating Scheduler without modifying existing YAML."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_TARGET, CONF_LABEL

class HeatingSchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Select the switch controlled by this scheduler instance."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            target = user_input[CONF_TARGET]
            if any(e.data.get(CONF_TARGET) == target for e in self._async_current_entries()):
                errors["base"] = "already_configured"
            elif not self.hass.states.get(target):
                errors["base"] = "missing_entity"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_LABEL) or f"Heating Scheduler ({target})",
                    data=user_input,
                )
        schema = vol.Schema({
            vol.Required(CONF_TARGET): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch")
            ),
            vol.Optional(CONF_LABEL, default="Heating"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
