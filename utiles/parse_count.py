from apscheduler.schedulers.background import BackgroundScheduler


class Counter:
    def __init__(self):
        self.count = 0

    def add_count(self):
        self.count += 1

    def reset_count(self):
        self.count = 0

    def get_count(self):
        return self.count


from config.chat_data import chat_data


class UserCount:
    def __init__(self):
        if not chat_data.get("UserCount"):
            chat_data["UserCount"] = {}
        self.data: dict[int, Counter] = chat_data['UserCount']

    def add_count(self, uid: int):
        if not self.data.get(uid):
            self.data[uid] = Counter()
        self.data[uid].add_count()
        self._save_to_chat_data()

    def get_count(self, uid: int):
        if not self.data.get(uid):
            return 0
        return self.data[uid].get_count()

    def reset_all_count(self):
        [i.reset_count() for i in self.data.values()]
        self._save_to_chat_data()

    def get_all_count(self):
        return sum([i.count for i in self.data.values()])

    def _save_to_chat_data(self):
        chat_data['UserCount'] = self.data


parse_count = UserCount()


def clear_regularly():
    scheduler = BackgroundScheduler()
    scheduler.add_job(parse_count.reset_all_count, 'cron', hour=0, minute=0)
    scheduler.start()


clear_regularly()
