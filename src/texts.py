"""Все тексты бота в одном месте — проще править копирайт без ловли строк по хендлерам."""

from __future__ import annotations


def welcome(company_name: str) -> str:
    return (
        f"👋 <b>Здравствуйте! Вас приветствует бот приема прайс-листов "
        f"компании {company_name}.</b>\n\n"
        "Я помогу вам быстро передать актуальные цены и остатки в нашу систему "
        "автоматизации. Это займет не более минуты.\n\n"
        "👇 Пожалуйста, нажмите кнопку <b>«Авторизоваться»</b> ниже, "
        "чтобы мы поняли, от какой компании поступает прайс."
    )


def welcome_known(company_name: str, supplier_name: str) -> str:
    return (
        f"👋 <b>С возвращением!</b>\n\n"
        f"Вы идентифицированы как представитель: <b>{supplier_name}</b>.\n"
        f"Компания-получатель: <b>{company_name}</b>.\n\n"
        "Можете сразу отправить новый прайс-лист или нажать «Обновить прайс»."
    )


def ask_company() -> str:
    return (
        "🏢 <b>Укажите, какую компанию вы представляете.</b>\n\n"
        "Введите ваше юридическое название или ИНН в ответном сообщении:"
    )


def identified(supplier_name: str) -> str:
    return (
        f"✅ <b>Спасибо! Вы успешно идентифицированы как представитель: "
        f"{supplier_name}.</b>\n\n"
        "Теперь вы можете отправить ваш актуальный прайс-лист."
    )


def pending_moderation(supplier_name: str) -> str:
    return (
        "⏳ <b>Заявка отправлена на проверку.</b>\n\n"
        f"Компания / ИНН: <b>{supplier_name}</b>\n\n"
        "Мы сообщим, как только менеджер одобрит доступ. "
        "Обычно это занимает немного времени."
    )


def already_pending(supplier_name: str) -> str:
    return (
        "⏳ <b>Ваша заявка уже на проверке.</b>\n\n"
        f"Компания / ИНН: <b>{supplier_name}</b>\n\n"
        "Дождитесь решения менеджера — мы пришлём уведомление."
    )


def approved_notify(supplier_name: str) -> str:
    return (
        f"✅ <b>Доступ одобрен!</b>\n\n"
        f"Вы идентифицированы как представитель: <b>{supplier_name}</b>.\n"
        "Осталось выбрать дни, когда вы будете присылать прайс — "
        "бот будет напоминать, если файла ещё нет."
    )


def ask_schedule(current: str | None = None) -> str:
    current_line = (
        f"\nСейчас: <b>{current}</b>\n" if current else "\n"
    )
    return (
        "📅 <b>Когда вы обычно присылаете прайс?</b>\n"
        f"{current_line}\n"
        "Отметьте дни недели или выберите пресет, затем нажмите "
        "<b>«Сохранить»</b>.\n"
        "В эти дни, если прайс ещё не прислан, бот напомнит."
    )


def schedule_saved(days_label: str) -> str:
    return (
        f"✅ <b>Расписание сохранено:</b> {days_label}.\n\n"
        "В выбранные дни напомним прислать прайс, если файла ещё нет."
    )


def schedule_need_days() -> str:
    return "Выберите хотя бы один день или пресет."


def admin_schedule_set(
    *,
    company_name: str,
    username: str | None,
    full_name: str,
    days_label: str,
) -> str:
    user_line = f"@{username}" if username else "—"
    return (
        "📅 <b>Поставщик задал расписание</b>\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Поставщик: <b>{company_name}</b>\n"
        f"• Дни прайса: <b>{days_label}</b>"
    )


def price_reminder(supplier_name: str) -> str:
    return (
        "⏰ <b>Напоминание о прайсе</b>\n\n"
        f"Сегодня по вашему расписанию нужно обновить прайс "
        f"(<b>{supplier_name}</b>).\n\n"
        "Пришлите файл Excel/CSV как <b>документ</b> — "
        "или нажмите «Обновить прайс»."
    )


def rejected_notify(supplier_name: str) -> str:
    return (
        "❌ <b>Заявка отклонена.</b>\n\n"
        f"Компания / ИНН: <b>{supplier_name}</b>\n\n"
        "Если это ошибка — нажмите «Авторизоваться» и укажите данные ещё раз "
        "или свяжитесь с менеджером."
    )


def moderation_request(
    *,
    company_name: str,
    username: str | None,
    full_name: str,
) -> str:
    user_line = f"@{username}" if username else "— (username не указан)"
    return (
        "🆕 <b>Новая заявка на авторизацию</b>\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Компания / ИНН: <b>{company_name}</b>\n\n"
        "Одобрить доступ?"
    )


def moderation_decided(
    *,
    approved: bool,
    company_name: str,
    username: str | None,
    full_name: str,
    moderator: str,
) -> str:
    user_line = f"@{username}" if username else "—"
    status = "✅ <b>Одобрено</b>" if approved else "❌ <b>Отклонено</b>"
    return (
        f"{status}\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Компания / ИНН: <b>{company_name}</b>\n"
        f"• Кем: {moderator}"
    )


def wait_for_file() -> str:
    return (
        "📊 <b>Ожидаю файл с прайс-листом.</b>\n\n"
        "<b>Требования к файлу:</b>\n"
        "• Формат: Excel (.xlsx, .xls) или CSV\n"
        "• Размер: до 20 МБ\n"
        "• Пожалуйста, отправляйте файл как <b>«Документ»</b> (без сжатия).\n\n"
        "Просто прикрепите и отправьте файл в этот чат. 👇"
    )


def success() -> str:
    return (
        "🎉 <b>Файл успешно принят!</b>\n\n"
        "Данные отправлены в отдел закупок и обновятся на нашем сайте/в системе "
        "в течение 15 минут. Спасибо за сотрудничество!"
    )


def bad_format(what: str, manager_contacts: str) -> str:
    return (
        "⚠️ <b>Ой, кажется, этот формат не поддерживается.</b>\n\n"
        "Я умею работать только с таблицами <b>Excel (.xlsx, .xls)</b> или "
        f"<b>CSV</b>. Вы прислали {what}.\n\n"
        "Пожалуйста, сохраните ваш прайс в формате Excel и пришлите его еще раз. "
        f"Если возникли трудности, {manager_contacts}."
    )


def need_auth() -> str:
    return (
        "🔐 Сначала нужно авторизоваться, чтобы мы поняли, "
        "от какой компании поступает прайс.\n\n"
        "Нажмите кнопку ниже или отправьте /start."
    )


def file_too_large() -> str:
    return (
        "⚠️ Файл слишком большой. Максимальный размер — <b>20 МБ</b>.\n"
        "Сожмите таблицу или разбейте на части и пришлите снова."
    )


def admin_caption(
    *,
    supplier_name: str,
    username: str | None,
    full_name: str,
    when: str,
) -> str:
    user_line = f"@{username}" if username else "—"
    return (
        "📥 <b>Новый прайс</b>\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Поставщик: <b>{supplier_name}</b>\n"
        f"• Время: {when}"
    )


def group_chat_id(chat_id: int, title: str | None = None) -> str:
    title_line = f"• Чат: <b>{title}</b>\n" if title else ""
    return (
        "👋 <b>Бот добавлен в чат</b>\n\n"
        f"{title_line}"
        f"• Chat ID: <code>{chat_id}</code>\n\n"
        "Скопируйте это значение в <code>ADMIN_CHAT_ID</code> в файле "
        "<code>.env</code> и перезапустите бота — сюда будут приходить прайсы."
    )
