# From https://github.com/Womsxd/ehArchiveD/blob/master/main.py

import asyncio
import json
import os
import random
import re
from typing import Union
from typing import List
import httpx
from dataclasses import dataclass

from loguru import logger

EHentaiURL = None


class EHentai:
    def __init__(self, cookies: list | str, proxy: str = None):
        self.eHentai_base_url = "https://e-hentai.org"
        self.exHentai_base_url = "https://exhentai.org"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 "
            "Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7",
            "origin": "https://e-hentai.org",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "referer": "",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "sec-gpc": "1",
            "Cookie": random.choice(cookies) if isinstance(cookies, list) else cookies,
        }
        self.proxy = proxy

        global EHentaiURL
        if EHentaiURL is None:
            EHentaiURL = self.check_ex_permission()
        self.eHentai_url = EHentaiURL

    @staticmethod
    def get_gid_from_url(url: str) -> Union["GUrl", None]:
        """从url中获取gid和token"""
        if match := re.search(r"(\d+)/([a-f0-9]+)", url):
            try:
                return GUrl(int(match[1]), match[2])
            except IndexError:
                return None
        raise

    async def get_archiver_info(self, gurl: Union["GUrl", str]) -> "GMetaData":
        """获取画廊元数据"""
        g = gurl if isinstance(gurl, GUrl) else self.get_gid_from_url(gurl)
        url = f"{self.eHentai_url}/api.php"
        body = {"method": "gdata", "gidlist": [[g.gid, g.token]], "namespace": 1}
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            response = await client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            try:
                result = response.json()
            except json.decoder.JSONDecodeError as error:
                raise IPBlocking() from error

            gmetadata = result.get("gmetadata", [])[0]
            torrents = [Torrent(**torrent) for torrent in gmetadata.pop("torrents", [])]
            return GMetaData(torrents=torrents, raw_json=result, **gmetadata)

    async def __archiver(self, archiver_info: "GMetaData", form_data: dict) -> str:
        """档案页面操作"""
        headers = self.headers.copy()
        url = f"{self.eHentai_url}/archiver.php?gid={archiver_info.gid}&token={archiver_info.token}&or={archiver_info.archiver_key}"
        headers["referer"] = url

        async with httpx.AsyncClient(proxy=self.proxy) as client:
            response = await client.post(
                url,
                headers=headers,
                data=form_data,
            )
        match response.status_code:
            case 200:
                return response.text
            case 302:
                raise UnableDownload()

    async def remove_download_url(self, archiver_info: "GMetaData") -> bool:
        """删除下载地址"""
        await self.__archiver(
            archiver_info,
            {"invalidate_sessions": "1"},
        )
        return True

    async def get_download_url(self, archiver_info: "GMetaData") -> str:
        """获取下载地址"""
        archiver = await self.__archiver(
            archiver_info,
            {
                "dltype": "org",
                "dlcheck": "Download+Original+Archive",
            },
        )
        match re.search(r'document\.location = "(.*?)";', archiver):
            case None:
                raise FailedGetDownloadUrl(archiver_info.gid)
            case match:
                return f"{match.group(1)}?start=1"

    async def get_required_gp(self, archiver_info: "GMetaData") -> int:
        """获取下载所需的GP"""
        archiver = await self.__archiver(archiver_info, {})
        match re.search(
            r'(?<=float:right">)(.*<strong>((\d+) GP|Free!))(?=</strong>)',
            archiver,
            re.DOTALL,
        ):
            case None:
                raise FaileGetGP()
            case match:
                return int(gp) if (gp := match.group(3)).isdigit() else 0

    @staticmethod
    def save_gallery_info(archiver_info: "GMetaData", output_path: str) -> str:
        """保存画廊信息"""
        op = os.path.join(output_path, f"{archiver_info.gid}.json")
        with open(op, "w", encoding="utf-8") as f:
            f.write(json.dumps(archiver_info.raw_json, ensure_ascii=False, indent=4))
        return op

    def check_ex_permission(self) -> str:
        """检查是否已经通过了exhentai的权限检查"""

        response = httpx.get(
            self.exHentai_base_url, headers=self.headers, proxy=self.proxy
        )
        if response.status_code == 200:
            if response.text != "":
                return self.exHentai_base_url
        else:
            logger.error("无法检查里站权限")
        return self.eHentai_base_url


# ================================== #
# ================================== #


@dataclass
class GUrl:
    gid: int
    token: str


@dataclass
class Torrent:
    hash: str
    added: str
    name: str
    tsize: str
    fsize: str


@dataclass
class GMetaData:
    def __init__(
        self,
        gid: int,
        token: str,
        archiver_key: str,
        title: str,
        title_jpn: str,
        category: str,
        thumb: str,
        uploader: str,
        posted: str,
        filecount: str,
        filesize: int,
        expunged: bool,
        rating: str,
        torrentcount: str,
        torrents: List[Torrent],
        tags: List[str],
        raw_json: dict,
        parent_gid: int = None,
        parent_key: str = None,
        first_gid: int = None,
        first_key: str = None,
        **kwargs,
    ):
        self.gid = gid
        self.token = token
        self.archiver_key = archiver_key
        self.title = title
        self.title_jpn = title_jpn
        self.category = category
        self.thumb = thumb
        self.uploader = uploader
        self.posted = posted
        self.filecount = filecount
        self.filesize = filesize
        self.expunged = expunged
        self.rating = rating
        self.torrentcount = torrentcount
        self.torrents = torrents
        self.tags = tags
        self.raw_json = raw_json
        self.parent_gid = parent_gid
        self.parent_key = parent_key
        self.first_gid = first_gid
        self.first_key = first_key
        self.kwargs = kwargs


class EHentaiError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class UnableDownload(EHentaiError):
    def __init__(self):
        super().__init__("账号无GP/下载流量，无法下载！")


class FailedGetDownloadUrl(EHentaiError):
    def __init__(self, gid: int):
        super().__init__(f"获取下载地址失败: {gid}")


class IPBlocking(EHentaiError):
    def __init__(self):
        super().__init__("IP已被Ehentai封锁，请更换代理")


class FaileGetGP(EHentaiError):
    def __init__(self):
        super().__init__("获取下载所需GP失败")


if __name__ == "__main__":
    cookie = ""
    e = EHentai(cookie)
    gurl = e.get_gid_from_url("https://e-hentai.org/g/2994353/a4f57a1001/")
    print(gurl)
    archiver_info = asyncio.run(e.get_archiver_info(gurl))
    print(archiver_info)
    required_gp = asyncio.run(e.get_required_gp(archiver_info))
    print(required_gp)
