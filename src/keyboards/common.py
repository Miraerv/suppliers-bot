from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.services.suppliers import WEEKDAY_LABELS

# callback_data — короткая строка, которую Telegram вернёт в CallbackQuery.
# Договоримся о namespace: action:payload
CB_AUTH = "auth:start"
CB_UPDATE_PRICE = "price:update"
CB_APPROVE_PREFIX = "auth:ok:"
CB_REJECT_PREFIX = "auth:no:"
CB_SCHEDULE = "sched:open"
CB_SCHEDULE_TOGGLE_PREFIX = "sched:t:"
CB_SCHEDULE_PRESET_PREFIX = "sched:p:"
CB_SCHEDULE_SAVE = "sched:save"
CB_SCHEDULE_CANCEL = "sched:cancel"

# Пресеты: id → дни недели
SCHEDULE_PRESETS: dict[str, frozenset[int]] = {
    "daily": frozenset(range(7)),
    "weekdays": frozenset({0, 1, 2, 3, 4}),
    "mon_thu": frozenset({0, 3}),
    "weekly": frozenset({0}),
}


def auth_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔐 Авторизоваться", callback_data=CB_AUTH)]
        ]
    )


def known_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Обновить прайс",
                    callback_data=CB_UPDATE_PRICE,
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Расписание",
                    callback_data=CB_SCHEDULE,
                )
            ],
        ]
    )


def moderation_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    """Кнопки модерации заявки в админ-группе."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"{CB_APPROVE_PREFIX}{telegram_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"{CB_REJECT_PREFIX}{telegram_id}",
                ),
            ]
        ]
    )


def schedule_keyboard(selected: set[int] | frozenset[int]) -> InlineKeyboardMarkup:
    """Календарь дней недели + пресеты + сохранить."""
    day_row: list[InlineKeyboardButton] = []
    for i, label in enumerate(WEEKDAY_LABELS):
        mark = "✓" if i in selected else "·"
        day_row.append(
            InlineKeyboardButton(
                text=f"{mark}{label}",
                callback_data=f"{CB_SCHEDULE_TOGGLE_PREFIX}{i}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            day_row[:4],
            day_row[4:],
            [
                InlineKeyboardButton(
                    text="Каждый день",
                    callback_data=f"{CB_SCHEDULE_PRESET_PREFIX}daily",
                ),
                InlineKeyboardButton(
                    text="Пн–Пт",
                    callback_data=f"{CB_SCHEDULE_PRESET_PREFIX}weekdays",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Пн и Чт",
                    callback_data=f"{CB_SCHEDULE_PRESET_PREFIX}mon_thu",
                ),
                InlineKeyboardButton(
                    text="Раз в неделю (Пн)",
                    callback_data=f"{CB_SCHEDULE_PRESET_PREFIX}weekly",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Сохранить",
                    callback_data=CB_SCHEDULE_SAVE,
                ),
            ],
        ]
    )
