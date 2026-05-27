import aiohttp
from datetime import datetime

from .exceptions import ThiinkConnectionError
from .models import BatteryDetails, EmsData, GridDetails, PhaseValues, ScheduleEntry, StatusData


class ThiinkClient:
    """Async HTTP client for the Thiink Control Unit local API."""

    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        self._base = base_url.rstrip("/")
        self._session = session

    async def get_ems(self) -> EmsData:
        """Fetch /data?state=ems — energy management data."""
        raw = await self._get("/data?state=ems")
        d = raw["data"]
        gd = d["grid_details"]
        return EmsData(
            grid_power=d["grid"],
            pv_power=d["pv"],
            battery_power=d["battery"],
            load_power=d["load"],
            soc=d["soc"],
            grid=GridDetails(
                voltage=PhaseValues(**gd["voltage"]),
                power=PhaseValues(**gd["power"]),
                current=PhaseValues(**gd["current"]),
                energy_import=gd["energy"]["in"],
                energy_export=gd["energy"]["out"],
            ),
            battery=BatteryDetails(
                capacity=d["battery_details"]["capacity"],
                voltage=d["battery_details"]["voltage"],
            ),
            inverter_temperature=d["temp"]["inverter"],
            battery_temperature=d["temp"]["battery"],
        )

    async def get_status(self) -> StatusData:
        """Fetch /data — device status."""
        raw = await self._get("/data")
        return StatusData(
            cabinet_temperature=raw["internal"]["temperature"],
            cabinet_humidity=raw["internal"]["humidity"],
            fw_version=raw["info"]["fw_version"],
            hw_version=raw["info"]["hw_version"],
            device_id=raw["info"]["device_id"],
            eth_status=raw["eth"]["status"],
        )

    async def get_schedule(self) -> list[ScheduleEntry]:
        """Fetch /data?key=schedule — EMS schedule slots."""
        raw = await self._get("/data?key=schedule")
        entries = [
            ScheduleEntry(
                mode=e["mode"],
                dispatch=e["dispatch"],
                trig_charge=e["trig_charge"],
                trig_discharge=e["trig_discharge"],
                max_charge=e["max_charge"],
                max_discharge=e["max_discharge"],
                max_export=e["max_export"],
                max_import=e["max_import"],
                min_soc=e["min_soc"],
                max_soc=e["max_soc"],
                hysteresis=e["hysteresis"],
                start_at=datetime.fromisoformat(e["start_at"]),
                active=e.get("active", False),
            )
            for e in raw
            if e.get("type") == "ems"
        ]
        entries.sort(key=lambda entry: entry.start_at)
        return entries

    async def _get(self, path: str) -> dict:
        url = f"{self._base}{path}"
        timeout = aiohttp.ClientTimeout(total=5)
        for attempt in range(2):
            try:
                async with self._session.get(url, timeout=timeout) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
                    return data
            except aiohttp.ClientError as err:
                if isinstance(err, aiohttp.ServerDisconnectedError) and attempt == 0:
                    # The device closed the TCP connection, retry once with fresh connection.
                    continue
                raise ThiinkConnectionError(f"Cannot reach device at {self._base}: {err}") from err
