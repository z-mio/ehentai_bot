from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("请发送画廊链接\n例: `https://e-hentai.org/g/2936195/178b3c5fec`")
