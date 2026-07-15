# Suppliers Bot — приёмщик прайсов

Telegram-бот для приёма прайс-листов от поставщиков (aiogram 3).

## Что делает

1. **Авторизация** — поставщик указывает компанию / ИНН (кнопка «Авторизоваться»).
2. **Модерация** — заявка уходит в чат закупок с `@username`, ИНН и кнопками «Одобрить» / «Отклонить».
3. **Календарь** — поставщик выбирает дни недели для прайса; бот напоминает, если файла нет.
4. **Приём файла** — только после одобрения; `.xlsx`, `.xls`, `.csv`, до 20 МБ, как документ.
5. **Маршрутизация** — файл сохраняется как `ИмяПоставщика_ДатаВремя.ext` и уходит в чат закупок.
6. **Память** — `telegram_id → компания + статус + расписание` в SQLite.

## Быстрый старт (Docker + Makefile)

Как у `bots/supplier`: основной способ запуска — Docker Compose через Makefile.

```bash
cp .env.example .env
# заполни BOT_TOKEN и ADMIN_CHAT_ID

make init    # pull + build + up
# или по шагам:
make build
make up

make logs    # логи
make down    # остановить
make restart # перезапуск
```

`./data` монтируется в контейнер (`suppliers.db` + `prices/`) и переживает рестарты.

### Локально без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python main.py
```

### ADMIN_CHAT_ID

1. Создай группу/канал для закупок.
2. Добавь бота в группу (для канала — админом с правом постить).
3. Бот сам пришлёт **Chat ID** в этот чат — скопируй его в `ADMIN_CHAT_ID` в `.env` и перезапусти (`make restart` или `make down && make up`).
4. Для супергрупп ID обычно вида `-100…`. (ID также пишется в лог, если бот не может писать в чат.)

## Сценарий

| Шаг | Update | Ответ |
|-----|--------|--------|
| `/start` (новый) | Message | Приветствие + кнопка «Авторизоваться» |
| Кнопка | CallbackQuery | Запрос названия компании / ИНН |
| Текст компании | Message + FSM | Заявка pending + уведомление в группу |
| Одобрить / Отклонить | CallbackQuery в группе | Статус + запрос расписания поставщику |
| Выбор дней / пресет | CallbackQuery | `schedule_days` в SQLite |
| 10:00 и 15:00 (Якутск) | APScheduler | Напоминание, если день в календаре и прайса нет |
| Документ xlsx/xls/csv | Message | Успех + `last_price_at` (напоминание в этот день больше не шлём) |
| `/start` (одобренный) | Message | Сразу «Обновить прайс» / ждать файл |
| `/start` (на проверке) | Message | «Заявка уже на проверке» |
| Добавление в группу | my_chat_member | Сообщение с Chat ID для `ADMIN_CHAT_ID` |

## Структура (зачем так)

```
main.py                 # точка входа: Bot + Dispatcher + polling
Dockerfile              # python:3.14-slim + main.py
docker-compose.yml      # сервис suppliers-bot, volume ./data
Makefile                # init / up / down / logs / build / restart
src/
  config.py             # env → Config
  texts.py              # все тексты
  middlewares.py        # DI: config, suppliers в handler data
  states/               # FSM-состояния (шаг диалога)
  keyboards/            # inline-кнопки + callback_data
  handlers/             # реакция на updates (тонкий слой)
  services/
    suppliers.py        # SQLite: кто этот telegram user
    files.py            # валидация / имя файла
    routing.py          # куда уехал прайс (чат; позже 1С/S3)
data/                   # suppliers.db + prices/ (в .gitignore, volume)
```

### aiogram «изнутри» (коротко)

- **Update** — JSON от Telegram (message / callback_query / …).
- **Dispatcher + Router** — цепочка фильтров → хендлер.
- **Bot** — HTTP-клиент к `api.telegram.org/bot<token>/METHOD`.
- **Polling** — цикл `getUpdates` с long timeout.
- **FSM** — «на каком шаге диалога»; storage по ключу user/chat.
- **Middleware** — код до/после хендлера; у нас кладёт зависимости в `data`.

## Дальше (не в MVP)

- Загрузка в 1С / S3 / Google Drive в `services/routing.py`
- Redis FSM storage при нескольких инстансах
- Webhook вместо polling
- Админ-команды: список поставщиков, смена привязки
- Более строгая проверка структуры Excel (колонки SKU/цена)

## Переменные окружения

См. `.env.example`.
