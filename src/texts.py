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


def ask_inn() -> str:
    return (
        "🏢 <b>Шаг 1 из 2 — введите ИНН вашей компании.</b>\n\n"
        "ИНН должен состоять из 10 или 12 цифр.\n"
        "Если ИНН нет — напишите <b>-</b> (минус), чтобы пропустить.\n\n"
        "Введите ИНН в ответном сообщении:"
    )


def bad_inn() -> str:
    return (
        "⚠️ Некорректный ИНН. ИНН должен состоять из 10 или 12 цифр.\n"
        "Если ИНН нет — напишите <b>-</b> (минус), чтобы пропустить.\n"
        "Пожалуйста, проверьте и введите ещё раз."
    )


def ask_company_name() -> str:
    return (
        "🏢 <b>Шаг 2 из 2 — введите название компании.</b>\n\n"
        "Укажите юридическое название организации в ответном сообщении:"
    )


def bad_company_name() -> str:
    return (
        "⚠️ Слишком короткое название. Введите полное юридическое название компании."
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
    inn: str | None,
    username: str | None,
    full_name: str,
) -> str:
    user_line = f"@{username}" if username else "— (username не указан)"
    inn_line = f"\n• ИНН: <b>{inn}</b>" if inn else ""
    return (
        "🆕 <b>Новая заявка на авторизацию</b>\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Компания / ИНН: <b>{company_name}</b>{inn_line}\n\n"
        "Одобрить доступ?"
    )


def moderation_decided(
    *,
    approved: bool,
    company_name: str,
    inn: str | None,
    username: str | None,
    full_name: str,
    moderator: str,
) -> str:
    user_line = f"@{username}" if username else "—"
    inn_line = f"\n• ИНН: <b>{inn}</b>" if inn else ""
    status = "✅ <b>Одобрено</b>" if approved else "❌ <b>Отклонено</b>"
    return (
        f"{status}\n\n"
        f"• Username: {user_line}\n"
        f"• Имя: {full_name}\n"
        f"• Компания: <b>{company_name}</b>{inn_line}\n"
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
        "в течение 15 минут. Спасибо за сотрудничество!\n\n"
        "💬 Хотите добавить комментарий к прайсу? Просто напишите сообщение — "
        "оно отправится менеджеру."
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


def help_supplier(company_name: str) -> str:
    return (
        f"📖 <b>Справка — бот приёма прайсов ({company_name})</b>\n\n"
        "<b>Команды:</b>\n"
        "• /start — начать / вернуться в начало\n"
        "• /help — эта справка\n\n"
        "<b>Как отправить прайс:</b>\n"
        "1. Нажмите «Авторизоваться» и укажите компанию или ИНН\n"
        "2. Дождитесь одобрения менеджером\n"
        "3. Выберите дни, когда обычно присылаете прайс\n"
        "4. Пришлите файл Excel/CSV как <b>документ</b> (не фото)\n\n"
        "Форматы: <b>.xlsx, .xls, .csv</b>, до 20 МБ."
    )


def help_admin() -> str:
    return (
        "📖 <b>Справка — админ-команды</b>\n\n"
        "Работают в этом чате (группа закупок):\n\n"
        "• /suppliers — список всех поставщиков\n"
        "• /bind <code>&lt;telegram_id&gt; &lt;компания&gt; [ИНН]</code> — "
        "создать или сменить привязку (сразу approved)\n"
        "• /unbind <code>&lt;telegram_id&gt;</code> — удалить привязку\n"
        "• /migrate_topics — создать темы для поставщиков без темы\n"
        "• /help — эта справка\n\n"
        "<b>Примеры:</b>\n"
        "<code>/bind 123456789 ООО Ромашка</code>\n"
        "<code>/bind 123456789 ООО Ромашка 7707083893</code>\n"
        "<code>/unbind 123456789</code>\n\n"
        "telegram_id можно взять из /suppliers или из профиля пользователя."
    )


def admin_suppliers_empty() -> str:
    return "📋 Поставщиков пока нет."


def admin_suppliers_header(total: int) -> str:
    return f"📋 <b>Поставщики</b> ({total}):\n"


def admin_supplier_line(
    *,
    index: int,
    company_name: str,
    inn: str | None,
    status: str,
    telegram_id: int,
    username: str | None,
    full_name: str | None,
    schedule_label: str,
) -> str:
    status_labels = {
        "approved": "✅ approved",
        "pending": "⏳ pending",
        "rejected": "❌ rejected",
    }
    status_text = status_labels.get(status, status)
    user_line = f"@{username}" if username else "—"
    name = full_name or "—"
    inn_line = f" · ИНН: {inn}" if inn else ""
    return (
        f"\n<b>{index}. {company_name}</b> — {status_text}\n"
        f"   id: <code>{telegram_id}</code> · {user_line} · {name}{inn_line}\n"
        f"   расписание: {schedule_label}"
    )


def admin_bind_usage() -> str:
    return (
        "Использование:\n"
        "<code>/bind &lt;telegram_id&gt; &lt;компания&gt; [ИНН]</code>\n\n"
        "Пример: <code>/bind 123456789 ООО Ромашка 7707083893</code>"
    )


def admin_unbind_usage() -> str:
    return (
        "Использование:\n"
        "<code>/unbind &lt;telegram_id&gt;</code>\n\n"
        "Пример: <code>/unbind 123456789</code>"
    )


def admin_bind_ok(
    *,
    telegram_id: int,
    company_name: str,
    status: str,
    created: bool,
) -> str:
    action = "создана" if created else "обновлена"
    return (
        f"✅ <b>Привязка {action}</b>\n\n"
        f"• telegram_id: <code>{telegram_id}</code>\n"
        f"• компания: <b>{company_name}</b>\n"
        f"• статус: <b>{status}</b>"
    )


def admin_unbind_ok(telegram_id: int, company_name: str) -> str:
    return (
        f"🗑 <b>Привязка удалена</b>\n\n"
        f"• telegram_id: <code>{telegram_id}</code>\n"
        f"• была компания: <b>{company_name}</b>"
    )


def admin_unbind_not_found(telegram_id: int) -> str:
    return f"Привязка для <code>{telegram_id}</code> не найдена."


def admin_bad_telegram_id() -> str:
    return "Некорректный telegram_id — нужен числовой ID пользователя."


def admin_bind_notify(company_name: str) -> str:
    return (
        f"✅ Менеджер привязал вас к компании: <b>{company_name}</b>.\n\n"
        "Можете отправить прайс-лист или настроить расписание через /start."
    )


def admin_unbind_notify() -> str:
    return (
        "ℹ️ Ваша привязка к компании снята менеджером.\n"
        "Чтобы снова отправлять прайсы, пройдите авторизацию через /start."
    )


def admin_migrate_topics(*, created: int, errors: int) -> str:
    parts = [f"📋 <b>Миграция тем завершена</b>\n\nСоздано тем: <b>{created}</b>"]
    if errors:
        parts.append(f"\nОшибок: <b>{errors}</b> — проверьте логи.")
    return "".join(parts)
