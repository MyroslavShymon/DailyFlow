from aiogram import Router, Dispatcher

from daily_flow.app.container import build_container
from daily_flow.config.db import load_db_settings

dp = Dispatcher()
router = Router()

settings = load_db_settings()
c = build_container(settings)

