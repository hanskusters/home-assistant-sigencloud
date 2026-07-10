import json
import logging
import time
import aiohttp

from .const import (
    BASE_URL,
    AUTH_ENDPOINT,
    SPIKE_LOAD_ENDPOINT,
    AUTOMATION_LOAD_RECORD_ENDPOINT,
    AUTOMATION_LOAD_DELETE_ENDPOINT,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class SigenCloudApiError(Exception):
    pass


class SigenCloudApi:
    def __init__(self, username: str, password: str, station_id: int) -> None:
        self._username = username
        self._password = password
        self._station_id = station_id
        self._token: str | None = None
        self._token_expires_at: float | None = None
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
        return self._session

    async def login(self) -> None:
        session = self._get_session()
        try:
            resp = await session.post(
                f"{BASE_URL}{AUTH_ENDPOINT}",
                json={"username": self._username, "password": self._password},
            )
        except aiohttp.ClientError as err:
            raise SigenCloudApiError(f"Connection error during login: {err}") from err

        if resp.status != 200:
            raise SigenCloudApiError(f"Login failed with status {resp.status}")

        data = await resp.json()

        raw = data.get("data", {})
        if isinstance(raw, str):
            raw = json.loads(raw)
        token = raw.get("accessToken")
        if not token:
            raise SigenCloudApiError(f"Could not find accessToken in login response: {data}")

        self._token = token
        expires_in = raw.get("expiresIn")
        if expires_in is not None:
            # Refresh 60 seconds before actual expiry
            self._token_expires_at = time.monotonic() + int(expires_in) - 60
            _LOGGER.debug("Token acquired, expires in %s seconds", expires_in)
        else:
            self._token_expires_at = None

    def _token_needs_refresh(self) -> bool:
        """Return True if the token is absent or will expire within the buffer window."""
        if self._token is None:
            return True
        if self._token_expires_at is None:
            return False
        return time.monotonic() >= self._token_expires_at

    @property
    def refresh_in(self) -> float | None:
        """Seconds until the token should be proactively refreshed. None if unknown."""
        if self._token_expires_at is None:
            return None
        return max(0.0, self._token_expires_at - time.monotonic())

    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        if self._token_needs_refresh():
            _LOGGER.debug("Token absent or nearing expiry, refreshing proactively")
            await self.login()

        session = self._get_session()
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        request_kwargs = {"headers": headers}
        if params is not None:
            request_kwargs["params"] = params
        if payload is not None:
            request_kwargs["json"] = payload

        try:
            resp = await session.request(method, f"{BASE_URL}{endpoint}", **request_kwargs)
        except aiohttp.ClientError as err:
            raise SigenCloudApiError(f"Connection error: {err}") from err

        if resp.status not in (200, 201):
            body = await resp.text()
            _LOGGER.error(
                "SigenCloud API error | %s %s | body: %s | query: %s | response %s: %s",
                method,
                f"{BASE_URL}{endpoint}",
                payload,
                resp.url.query_string,
                resp.status,
                body,
            )
            raise SigenCloudApiError(f"Request failed with status {resp.status}: {body}")

        return await resp.json(content_type=None)

    async def add_spike_load(
        self,
        load_type: int,
        start_time: str,
        start_date: str,
        duration: int,
        power: float,
    ) -> dict:
        payload = {
            "stationId": self._station_id,
            "loadType": load_type,
            "startTime": start_time,
            "startDate": start_date,
            "duration": duration,
            "power": power,
        }
        return await self._request("POST", SPIKE_LOAD_ENDPOINT, payload)

    async def get_spike_loads(self) -> list | None:
        endpoint = AUTOMATION_LOAD_RECORD_ENDPOINT.format(
            station_id=self._station_id
        )
        response = await self._request(
            "GET",
            endpoint,
            params={"stationId": self._station_id},
        )
        if isinstance(response, dict) and isinstance(response.get("data"), list):
            return response["data"]
        return None

    async def remove_spike_load(self, event_id: str) -> dict:
        params = {"stationId": self._station_id, "eventId": event_id}
        return await self._request(
            "POST",
            AUTOMATION_LOAD_DELETE_ENDPOINT,
            params=params,
        )

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
