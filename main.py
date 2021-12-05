import asyncio
import json
import os
from sys import argv
from typing import Optional

import aiohttp


class Tag:
    out: str
    api: str
    type: str
    tag: str

    def __init__(self, out: str, api: str, type: str, tag: str):
        self.out = out
        self.api = api
        self.type = type
        self.tag = tag

        os.makedirs(self.file_path, exist_ok=True)

    @property
    def get_url(self) -> str:
        return os.path.join(self.api, self.tag)

    @property
    def file_path(self) -> str:
        return os.path.join(self.out, self.type, self.tag.removeprefix("img/"))

    async def image_url(self) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.get_url) as response:
                answer = await response.json()
                url = answer["url"]

                if self.exist(url):
                    return None

                return url

    def url_file(self, url: str) -> str:
        return os.path.join(self.file_path, url.split("/")[-1])

    def exist(self, url: str) -> bool:
        if os.path.exists(self.url_file(url)):
            return True
        return False

    async def download(self, url: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(self.url_file(url), "wb") as f:
                    async for chunk in response.content.iter_chunked(1024):
                        f.write(chunk)
        print(f"Downloaded - {self.url_file(url)}")


class Nekos:
    api: str = "https://nekos.life/api/v2/"
    tags: list[Tag]
    out: str

    def __init__(self, tags: dict[str, list[str]], out: str):
        self.tags = []
        self.out = out

        for type, tgs in tags.items():
            for tag in tgs:
                self.tags.append(Tag(self.out, self.api, type, tag))

    async def run(self) -> None:
        while True:
            try:
                for tag in self.tags:
                    url = await tag.image_url()
                    if url is not None:
                        await tag.download(await tag.image_url())
            except Exception:
                pass
            except KeyboardInterrupt:
                exit()


if __name__ == "__main__":
    with open("tags.json", "r") as file:
        tags = json.load(file)

    app = Nekos(tags, "downloads")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([app.run() for _ in range(int(argv[1]))]))
