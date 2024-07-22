from time import time

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class Counter:
    def __init__(self):
        self.now_count = 0
        self.day_count = 0
        self.request_time = 0
        self.day_require_gp = 0

    def add_count(self, gp=0):
        self.now_count += 1
        self.day_count += 1
        self.day_require_gp += gp
        self.request_time = time()

    def reset_now_count(self):
        self.now_count = 0
        self.request_time = 0

    def reset_day_count(self):
        self.day_count = 0
        self.day_require_gp = 0


from config.chat_data import chat_data


class UserCount:
    def __init__(self):
        if not chat_data.get("UserCount"):
            chat_data["UserCount"] = {}
        self.data: dict[int, Counter] = chat_data["UserCount"]

    def get_counter(self, uid: int):
        return self.init(uid)

    def reset_all_day_count(self):
        [i.reset_day_count() for i in self.data.values()]
        logger.info("已重置今日解析次数")

    def get_all_count(self):
        return sum(i.day_count for i in self.data.values())

    def get_all_gp(self):
        return sum(i.day_require_gp for i in self.data.values())

    def init(self, uid: int):
        if not self.data.get(uid):
            self.data[uid] = Counter()
        return self.data[uid]


parse_count = UserCount()


def clear_regularly():
    scheduler = BackgroundScheduler()
    scheduler.add_job(parse_count.reset_all_day_count, "cron", hour=0, minute=0)
    scheduler.start()


clear_regularly()
