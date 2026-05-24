import aiohttp

from .exceptions import ThiinkConnectionError
from .models import BatteryDetails, EmsData, GridDetails, PhaseValues, ScheduleData, ScheduleEntry, StatusData


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

    async def get_schedule(self) -> ScheduleData:
        """Fetch /data?key=schedule — EMS schedule slots."""
        entries = await self._get("/data?key=schedule")
        active = next((e for e in entries if e.get("active") and e.get("type") == "ems"), None)
        if active is None:
            raise ThiinkConnectionError("No active EMS schedule entry found")
        return ScheduleData(
            active=ScheduleEntry(
                mode=active["mode"],
                dispatch=active["dispatch"],
                trig_charge=active["trig_charge"],
                trig_discharge=active["trig_discharge"],
                max_charge=active["max_charge"],
                max_discharge=active["max_discharge"],
                max_export=active["max_export"],
                max_import=active["max_import"],
                min_soc=active["min_soc"],
                max_soc=active["max_soc"],
                hysteresis=active["hysteresis"],
            )
        )

    async def _get(self, path: str) -> dict:
        try:
            async with self._session.get(
                f"{self._base}{path}",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise ThiinkConnectionError(f"Cannot reach device at {self._base}: {err}") from err
