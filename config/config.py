# -*- coding: UTF-8 -*-

from pathlib import Path
from typing import Optional, Any

import yaml

DP = Path("data")
DP.mkdir(exist_ok=True, parents=True)


class BaseConfig:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path
        self.config = self.load_config()
        self._key_map = {}

    def load_config(self):
        with open(self.cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_config(self):
        with open(self.cfg_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True)

    def retrieve(self, key: str, default: Optional[Any] = None) -> Any:
        keys = key.split(".")
        result = self.config
        for k in keys:
            if isinstance(result, dict):
                result = result.get(k, default)
            else:
                return default
        self._key_map[keys[-1]] = key  # 保存属性名到配置路径的映射
        return result

    def modify(self, key, value):
        # 根据key和value实现修改逻辑
        keys = key.split(".")
        temp = self.config
        for k in keys[:-1]:
            temp = temp.setdefault(k, {})
        temp[keys[-1]] = value
        self.save_config()


class Config(BaseConfig):
    def __setattr__(self, key, value):
        if key in self.__dict__ and key in self._key_map:
            self.modify(self._key_map[key], value)
        super().__setattr__(key, value)


class BotConfig(Config):
    def __init__(self, cfg_path):
        super().__init__(cfg_path)
        self.bot_token = self.retrieve("user.bot_token")
        self.api_id = self.retrieve("user.api_id")
        self.api_hash = self.retrieve("user.api_hash")
        self.hostname = self.retrieve("proxy.hostname")
        self.port = self.retrieve("proxy.port")
        self.scheme = self.retrieve("proxy.scheme")
        self.proxy = (
            f"{self.scheme}://{self.hostname}:{self.port}"
            if all([self.scheme, self.hostname, self.port])
            else None
        )


class EConfig(Config):
    def __init__(self, cfg_path):
        super().__init__(cfg_path)
        self.whitelist: list = self.retrieve("whitelist")
        self.admins: list = self.retrieve("admins")
        self.request_limit: int = self.retrieve("request_limit")
        self.total_request_limit: int = self.retrieve("total_request_limit")
        self.time_limit: int = self.retrieve("time_limit")
        self.destroy_regularly: int = self.retrieve("destroy_regularly")
        self.cookies: list = self.retrieve("cookies")
        self.disable: bool = self.retrieve("disable")
        self.download: bool = self.retrieve("download")


bot_cfg = BotConfig("bot.yaml")
e_cfg = EConfig("./config/config.yaml")
