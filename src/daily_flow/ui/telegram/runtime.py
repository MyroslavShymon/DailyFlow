from aiogram import Dispatcher, Router

from daily_flow.ui.telegram.middlewares.auth_middleware import AuthMiddleware

router = Router()

dp = Dispatcher()

dp.message.outer_middleware(AuthMiddleware())
