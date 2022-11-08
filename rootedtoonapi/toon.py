"""Asynchronous Python client for a rooted Toon."""
from __future__ import annotations

import asyncio
import json
import socket
from typing import Any, Dict, Optional

import aiohttp
import async_timeout
import backoff
from yarl import URL

from .const import (
    ENERGY_DEVICE,
    PROGRAM_STATE_OVERRIDE,
    THERMOSTAT_DEVICE,
    TOON_API_BASE_PATH,
    TOON_API_SCHEME,
)
from .exceptions import (
    ToonConnectionError,
    ToonConnectionTimeoutError,
    ToonError,
    ToonRateLimitError,
)
from .models import Status


class Toon:
    """Main class for handling connections with the Quby ToonAPI."""

    _status: Optional[Status] = None
    _close_session: bool = False

    def __init__(
            self,
            host: str,
            *,
            port: int = 80,
            request_timeout: int = 10,
            session: Optional[aiohttp.client.ClientSession] = None,
    ) -> None:
        """Initialize connection with the Quby ToonAPI."""
        self._session = session

        self.request_timeout = request_timeout
        self.host = host
        self.port = port

        self._status = Status()

    @backoff.on_exception(backoff.expo, ToonConnectionError, max_tries=3, logger=None)
    @backoff.on_exception(
        backoff.expo, ToonRateLimitError, base=60, max_tries=6, logger=None
    )
    async def _request(
        self,
        device: str,
        action: str,
        *,
        query: Optional[Dict[str: Any]] = {},
        data: Optional[Any] = None,
        method: str = "GET",
    ) -> Any:
        """Handle a request to the Rooted Toon."""

        query = {
            "action": action,
            **query
        }
        path = TOON_API_BASE_PATH + device
        url = URL.build(
            scheme=TOON_API_SCHEME,
            host=self.host,
            port=self.port,
            path=path,
            query=query
        )

        headers = {
            "Accept": "application/json",
        }

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method, url, json=data, headers=headers, ssl=True,
                )
        except asyncio.TimeoutError as exception:
            raise ToonConnectionTimeoutError(
                "Timeout occurred while connecting to the Toon"
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ToonConnectionError(
                "Error occurred while communicating with the Toon"
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        # Error handling
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if response.status == 429:
                raise ToonRateLimitError(
                    "Rate limit error has occurred with the Toon"
                )

            if content_type == "application/json":
                raise ToonError(response.status, json.loads(contents.decode("utf8")))
            raise ToonError(response.status, {"message": contents.decode("utf8")})

        # Handle empty response
        if response.status == 204:
            return

        if "text/javascript" in content_type:
            return await response.json(content_type="text/javascript")
        return await response.text()

    async def determine_devices(self):
        devices_data = await self._request(
            device=ENERGY_DEVICE,
            action="getDevices.json"
        )
        self._status.gas_usage.determine_device(devices_data)
        self._status.power_usage.determine_devices(devices_data)

    async def update_energy_meter(self, data: Dict[str, Any] = None) -> Optional[Status]:
        assert self._status
        if data is None:
            data = await self._request(
                device=ENERGY_DEVICE,
                action="getDevices.json"
            )
        self._status.gas_usage.update_from_dict(data)
        self._status.power_usage.update_from_dict(data)
        return self._status

    async def update_climate(self, data: Dict[str, Any] = None) -> Optional[Status]:
        """Get all information in a single call."""
        assert self._status
        if data is None:
            data = await self._request(
                device=THERMOSTAT_DEVICE,
                action="getThermostatInfo"
            )
        self._status.thermostat.update_from_dict(data)
        return self._status

    async def set_current_setpoint(self, temperature: float) -> None:
        """Set the target temperature for the thermostat."""
        query = {
            "Setpoint": round(temperature * 100),
        }

        await self._request(
            device=THERMOSTAT_DEVICE,
            action="setSetpoint",
            query=query,
        )
        await self.update_climate()

    async def set_active_state(
            self, active_state: int, program_state: int = PROGRAM_STATE_OVERRIDE
    ) -> None:
        """Set the active state for the thermostat"""
        query = {
            "state": program_state,
            "temperatureState": active_state
        }

        await self._request(
            device=THERMOSTAT_DEVICE,
            action="changeSchemeState",
            query=query
        )
        await self.update_climate()

    async def set_hvac_mode(self, program_state):
        """Set the hvac mode for the thermostat"""
        query: Dict[str: str] = { "state": program_state }

        await self._request(
            device=THERMOSTAT_DEVICE,
            action="changeSchemeState",
            query=query
        )
        await self.update_climate()

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Toon:
        """Async enter."""
        await self.determine_devices()
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
