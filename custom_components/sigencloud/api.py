import json
import logging
import aiohttp

from .const import BASE_URL, AUTH_ENDPOINT, SPIKE_LOAD_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class SigenCloudApiError(Exception):
    pass


class SigenCloudApi:
    def __init__(self, username: str, password: str, station_id: int) -> None:
        self._username = username
        self._password = password
        self._station_id = station_id
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
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

    async def _request(self, method: str, endpoint: str, payload: dict) -> dict:
        if self._token is None:
            await self.login()

        session = self._get_session()
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            resp = await session.request(
                method, f"{BASE_URL}{endpoint}", headers=headers, json=payload
            )
        except aiohttp.ClientError as err:
            raise SigenCloudApiError(f"Connection error: {err}") from err

        if resp.status == 401:
            _LOGGER.debug("Token expired, re-authenticating")
            await self.login()
            headers["Authorization"] = f"Bearer {self._token}"
            try:
                resp = await session.request(
                    method, f"{BASE_URL}{endpoint}", headers=headers, json=payload
                )
            except aiohttp.ClientError as err:
                raise SigenCloudApiError(f"Connection error after re-auth: {err}") from err

        if resp.status not in (200, 201):
            body = await resp.text()
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

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
