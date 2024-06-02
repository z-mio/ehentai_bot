import os

from loguru import logger
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup as Ikm,
    InlineKeyboardButton as Ikb,
    CallbackQuery,
)
from config.config import e_cfg, DP, bot_cfg
from utiles.download_file import download_file
from utiles.ehArchiveD import EHentai
from utiles.filter import is_admin
from utiles.parse_count import parse_count
from utiles.utile import is_admin_, rate_limit
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.start()


@Client.on_message(
    filters.regex(r"https://(?:e-|ex)hentai.org/g/(\d+)/([a-f0-9]+)") & filters.private
)
@rate_limit(request_limit=e_cfg.request_limit, time_limit=e_cfg.time_limit, total_request_limit=e_cfg.total_request_limit)
async def ep(_, msg: Message):
    if e_cfg.disable and not is_admin_(msg.from_user.id):
        return await msg.reply("解析功能暂未开放")
    m = await msg.reply('解析中...')
    try:
        archiver_info, d_url, json_path = await ehentai_parse(msg.text, True)
    except Exception as e:
        await m.edit(f"解析失败: {e}")
        raise e
    d = f"{archiver_info.gid}/{archiver_info.token}"
    btn = Ikm(
        [
            [
                Ikb("下载", f"download_{d}") if e_cfg.download else Ikb("下载", url=d_url),
                Ikb("销毁下载", callback_data=f"cancel_{d}"),
            ]
        ]
    )

    if not e_cfg.download and e_cfg.destroy_regularly:
        await destroy_regularly(msg.text)

    await msg.reply_document(json_path, quote=True, reply_markup=btn)
    await m.delete()

    parse_count.add_count(msg.from_user.id)
    logger.info(f"{msg.from_user.full_name} 归档 {msg.text} (今日 {parse_count.get_count(msg.from_user.id)} 个)")

    os.remove(json_path)


async def ehentai_parse(url: str, o_json: bool = False):
    """解析e-hentai画廊链接"""
    ehentai = EHentai(e_cfg.cookies, proxy=bot_cfg.proxy)
    archiver_info = await ehentai.get_archiver_info(url)
    d_url = await ehentai.get_download_url(archiver_info)

    if o_json:
        json_path = ehentai.save_gallery_info(archiver_info, DP)
        return archiver_info, d_url, json_path
    return archiver_info, d_url


async def cancel_download(url: str) -> bool:
    """销毁下载"""
    ehentai = EHentai(e_cfg.cookies, proxy=bot_cfg.proxy)
    archiver_info = await ehentai.get_archiver_info(url)
    return await ehentai.remove_download_url(archiver_info)


@Client.on_callback_query(filters.regex(r"^download_"))
async def download_archiver(_, cq: CallbackQuery):
    await cq.message.edit_reply_markup(Ikm([[Ikb("下载中...", "downloading")]]))
    gurl = cq.data.split("_")[1]
    try:
        archiver_info, d_url = await ehentai_parse(gurl)
        file = f"{archiver_info.gid}.zip"
        if not os.path.exists(file):
            """已存在则不再下载"""
            file = await download_file(d_url, file, proxy=bot_cfg.proxy)
    except Exception as e:
        await cq.message.reply(f"下载失败: {e}")
        raise e
    await cq.message.edit_reply_markup()
    await cq.message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)

    await cq.message.reply_document(file, quote=True)
    await cancel_download(gurl)


@Client.on_callback_query(filters.regex(r"^cancel_"))
async def cancel_dl(_, cq: CallbackQuery):
    gurl = cq.data.split("_")[1]
    logger.info(f"{cq.from_user.full_name} 销毁 {gurl}")
    if not (await cancel_download(gurl)):
        await cq.answer("销毁下载失败")
        s = "失败"
    else:
        await cq.message.edit_reply_markup()
        await cq.answer("已销毁下载")
        s = "成功"
    logger.info(f"{cq.from_user.full_name} 创建的 {gurl} 销毁{s}")


@Client.on_message(filters.command("count") & is_admin)
async def count(_, msg: Message):
    await msg.reply(f"今日解析次数: __{parse_count.get_all_count()}__")


async def destroy_regularly(url: str):
    """定时销毁下载"""
    scheduler.add_job(cancel_download, 'interval', args=[url], seconds=e_cfg.destroy_regularly)
