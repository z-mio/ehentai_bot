from typing import Callable

import aiofiles
import httpx

from config.config import DP


async def download_file(
    url: str,
    filename: str,
    *,
    proxy: str = None,
    proxies: dict[str, any] = None,
    progress: Callable = None,
    progress_args: tuple = (),
) -> str:
    """分块下载文件, 目录不存在会自动创建，progress接收两个参数: 已下载大小, 总大小"""
    async with httpx.AsyncClient(proxy=proxy, proxies=proxies) as client:
        async with client.stream("GET", url, follow_redirects=True) as r:
            r.raise_for_status()

            total_size = int(r.headers.get("Content-Length", 0))
            current = 0

            save_path = DP.joinpath(filename)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            if total_size > 10 * 1024 * 1024:  # 检查文件大小是否大于10MB
                async with aiofiles.open(save_path, "wb") as f:
                    async for chunk in r.aiter_bytes(chunk_size=10240):
                        await f.write(chunk)

                        current += len(chunk)
                        if progress:
                            await progress(current, total_size, *progress_args)
            else:
                content = await r.aread()  # 如果文件大小小于 10MB，请读取全部内容
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(content)

    return str(save_path)
