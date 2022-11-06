"""Asynchronous Python client for a rooted Toon."""
from __future__ import annotations

import asyncio
import json
import socket
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aiohttp
import async_timeout
import backoff
from yarl import URL

from .__version__ import __version__
from .const import (
    ACTIVE_STATE_OFF,
    PROGRAM_STATE_OVERRIDE,
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
        # uri: str = "",
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
        print(url)

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

    async def update_climate(self, data: Dict[str, Any] = None) -> Optional[Status]:
        """Get all information in a single call."""
        assert self._status
        if data is None:
            data = await self._request(
                device="happ_thermstat",
                action="getThermostatInfo"
            )
        self._status.thermostat.update_from_dict(data)
        return self._status

    async def set_current_setpoint(self, temperature: float) -> None:
        """Set the target temperature for the thermostat."""
        assert self._status
        query = {
            "Setpoint": round(temperature * 100),
        }

        data = {
            "currentSetpoint": round(temperature * 100),
            "programState": PROGRAM_STATE_OVERRIDE,
            "activeState": ACTIVE_STATE_OFF,
        }

        await self._request(
            device="happ_thermstat",
            action="setSetpoint",
            query=query,
        )
        self._status.thermostat.update_from_dict(data)

    async def set_active_state(
        self, active_state: int, program_state: int = PROGRAM_STATE_OVERRIDE
    ) -> None:
        """.."""
        assert self._status
        data = {
            "programState": program_state,
            "activeState": active_state
        }
        query = {
            "state": program_state,
            "temperatureState": active_state
        }

        await self._request(
            device="happ_thermstat",
            action="changeSchemeState",
            query=query
        )
        self._status.thermostat.update_from_dict(data)

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Toon:
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
