from pyrogram import Client, filters
from pyrogram.types import Message

from config.config import e_cfg
from utiles.filter import is_admin


@Client.on_message(filters.command("sw") & is_admin)
async def switch(_, msg: Message):
    disable = e_cfg.disable
    e_cfg.disable = not disable
    return await msg.reply_text(f"已{'关闭' if e_cfg.disable else '开启'}解析")


@Client.on_message(filters.command("d") & is_admin)
async def download_switch(_, msg: Message):
    download = e_cfg.download
    e_cfg.download = not download
    return await msg.reply_text(f"已{'开启' if e_cfg.download else '关闭'}下载")
