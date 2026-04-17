"""LeagueWeb API 客户端 — 各插件共用"""

import httpx
from nonebot import get_driver
from nonebot.log import logger

driver = get_driver()


def get_api_url() -> str:
    return getattr(driver.config, "league_api_url", "http://localhost:5000")


async def api_get(path: str, **kwargs) -> dict | list:
    async with httpx.AsyncClient(base_url=get_api_url(), timeout=10) as client:
        resp = await client.get(path, **kwargs)
        resp.raise_for_status()
        return resp.json()


async def api_post(path: str, json: dict | None = None, **kwargs) -> dict:
    async with httpx.AsyncClient(base_url=get_api_url(), timeout=10) as client:
        resp = await client.post(path, json=json, **kwargs)
        resp.raise_for_status()
        return resp.json()


async def api_put(path: str, json: dict | None = None, **kwargs) -> dict:
    async with httpx.AsyncClient(base_url=get_api_url(), timeout=10) as client:
        resp = await client.put(path, json=json, **kwargs)
        resp.raise_for_status()
        return resp.json()
