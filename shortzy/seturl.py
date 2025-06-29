import asyncio
import re
from urllib.parse import urlparse
import aiohttp


class SetURL:
    def __init__(self, api_key: str, base_site: str = "seturl.in"):
        self.api_key = api_key
        self.base_site = base_site
        self.base_url = f"https://{self.base_site}/api"

        if not self.api_key:
            raise Exception("API key not provided")

    async def __fetch(self, session: aiohttp.ClientSession, params: dict) -> dict:
        async with session.get(self.base_url, params=params, ssl=False) as response:
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                text = await response.text()
                return {"status": "error", "shortenedUrl": None, "message": text}

    async def convert(self, link: str, alias: str = "", silently_fail: bool = False, quick_link: bool = False, **kwargs) -> str:
        if await self.is_short_link(link):
            return link

        if quick_link:
            return await self.get_quick_link(link)

        params = {
            "api": self.api_key,
            "url": link,
            "format": "json"
        }

        if alias:
            params["alias"] = alias

        try:
            async with aiohttp.ClientSession() as session:
                data = await self.__fetch(session, params)
                if "shortenedUrl" in data:
                    return data["shortenedUrl"]
                elif silently_fail:
                    return link
                else:
                    raise Exception(data.get("message", "Unknown error"))
        except Exception as e:
            if silently_fail:
                return link
            raise e

    async def get_quick_link(self, link: str, alias: str = "") -> str:
        url = f"https://{self.base_site}/api?api={self.api_key}&url={link}&alias={alias}&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                try:
                    data = await response.json()
                    return data.get("shortenedUrl") or link
                except:
                    return link
