from aiogram import Router

from src.handlers import admin, auth, chat, group, price, schedule, start


def setup_routers() -> Router:
    """Корневой роутер. Порядок важен: более специфичные фильтры — раньше."""
    root = Router(name="root")
    root.include_router(start.router)
    root.include_router(admin.router)
    root.include_router(auth.router)
    root.include_router(schedule.router)
    root.include_router(price.router)
    root.include_router(chat.router)
    root.include_router(group.router)
    return root
