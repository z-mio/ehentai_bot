from collections import defaultdict
from time import time

from pyrogram import Client
from pyrogram.types import Message, ChosenInlineResult

from config.config import e_cfg
from utiles.parse_count import parse_count


def is_admin_(user_id: int) -> bool:
    return user_id in e_cfg.admins


requests = defaultdict(int)
last_request_time = defaultdict(int)


# 速率限制
def rate_limit(request_limit=3, time_limit=60, total_request_limit=100, group: bool = False):
    def decorator(func):
        async def wrapper(client: Client, message: Message | ChosenInlineResult):
            user_id = (
                message.chat.id
                if group
                else (message.from_user or message.sender_chat).id
            )
            if user_id in e_cfg.whitelist or user_id in e_cfg.admins or e_cfg.disable:
                # 白名单用户或管理员不受速率限制
                return await func(client, message)
            if parse_count.get_all_count() >= total_request_limit:
                return await message.reply("Bot今日解析次数已达上限，明天再来吧")

            current_time = time()
            time_left = time_limit - (current_time - last_request_time[user_id])
            if current_time - last_request_time[user_id] > time_limit:
                requests[user_id] = 1
                last_request_time[user_id] = int(current_time)
            else:
                if requests[user_id] >= request_limit:
                    if isinstance(message, Message):
                        if group and message.chat.type.value in ["group", "supergroup"]:
                            return await message.reply(
                                f"群组速率限制：`{request_limit}`次 / {time_format(time_limit)} | 还需等待：{time_format(time_left)}"
                            )
                        else:
                            return await message.reply(
                                f"速率限制：`{request_limit}`次 / {time_format(time_limit)} | 还需等待：{time_format(time_left)}"
                            )
                    elif isinstance(message, ChosenInlineResult):
                        return await client.edit_inline_text(
                            message.inline_message_id,
                            f"速率限制：`{request_limit}`次 / {time_format(time_limit)} | 还需等待：{time_format(time_left)}",
                        )
                requests[user_id] += 1

            await func(client, message)

        return wrapper

    return decorator


def time_format(s):
    if s < 60:
        return f"`{s:.0f}`秒"
    elif 60 <= s < 3600:
        return f"`{s / 60:.0f}`分钟"
    else:
        return f"`{s / 3600:.0f}`小时"
