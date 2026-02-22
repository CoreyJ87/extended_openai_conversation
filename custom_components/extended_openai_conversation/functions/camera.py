"""Camera function for capturing and analyzing camera snapshots."""

from __future__ import annotations

import base64
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.camera import async_get_image
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base import Function

_LOGGER = logging.getLogger(__name__)

CAMERA_IMAGE_KEY = "__camera_image__"


class CameraFunction(Function):
    """Captures a camera snapshot and returns it as an image for vision analysis."""

    def __init__(self) -> None:
        super().__init__(vol.Schema({}))

    async def execute(
        self,
        hass: HomeAssistant,
        function_config: dict[str, Any],
        arguments: dict[str, Any],
        llm_context: llm.LLMContext | None,
        exposed_entities: list[dict[str, Any]],
    ) -> Any:
        entity_id: str | None = arguments.get("entity_id")
        if not entity_id:
            return "Error: entity_id is required"

        if hass.states.get(entity_id) is None:
            return f"Error: camera entity '{entity_id}' not found"

        try:
            image = await async_get_image(hass, entity_id)
        except Exception as err:
            _LOGGER.error("Failed to get camera image for %s: %s", entity_id, err)
            return f"Error: Could not capture snapshot from {entity_id}: {err}"

        b64 = base64.b64encode(image.content).decode()
        mime = image.content_type or "image/jpeg"

        _LOGGER.debug("Captured camera snapshot from %s (%s, %d bytes)", entity_id, mime, len(image.content))

        return {
            CAMERA_IMAGE_KEY: True,
            "url": f"data:{mime};base64,{b64}",
            "entity_id": entity_id,
        }
