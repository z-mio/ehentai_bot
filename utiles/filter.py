from pyrogram import filters
from config.config import e_cfg

is_admin = filters.user(e_cfg.admins)
