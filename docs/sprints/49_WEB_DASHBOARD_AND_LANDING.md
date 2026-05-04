# Sprint 49: Web Dashboard & Landing Page (FastAPI + Tailwind)

**Status:** `Draft`
**Date Proposed:** 2026-05-04
**Objective:** Evolve Pulse Monolith from a pure Telegram bot into a full-fledged SaaS platform with a web-based dashboard and marketing landing page, utilizing our existing PostgreSQL database and FastAPI core.

## 🎯 Architecture
To keep development "LLM-friendly" and maintainable without complex JavaScript build steps (Webpack/npm), we will use a pure Python-driven monolithic stack:
- **Backend:** FastAPI (already running our webhooks, will now serve HTML templates).
- **Frontend:** Pure HTML + Tailwind CSS (via CDN) + Jinja2 Templates.
- **Charts:** Chart.js or ApexCharts injected directly into HTML.
- **Auth:** Telegram Login Widget (seamless integration with existing user DB).

## 📋 Tasks

### [Infrastructure & Routing]
- [ ] Reconfigure `Caddyfile` so that root `/` goes to the landing page, `/app` goes to the dashboard, and `/webhook` continues to go to the bot logic.
- [ ] Add `jinja2` to `requirements.txt` and configure FastAPI `Jinja2Templates` directory (`src/web/templates`).

### [Authentication (Telegram Login)]
- [ ] Create `/auth/telegram` route in FastAPI to verify the cryptographic hash sent by the Telegram Login Widget using `TELEGRAM_BOT_TOKEN`.
- [ ] Set secure, HTTP-only JWT cookies for the user session upon successful login.
- [ ] Create an `auth_required` dependency for FastAPI dashboard routes.

### [Views & Frontend]
- [ ] **Landing Page (`/`)**: Dark-themed cyberpunk/monolith aesthetic. Explains the product philosophy. Includes the Telegram Login button.
- [ ] **Dashboard (`/app`)**: Main user view. 
  - Visual grid of Active Projects.
  - Heatmap or Bar Chart of Focus Time for the last 14 days.
  - Interactive "Daily Report" historical viewer.

## 🔒 Security Notes
- All web sessions must be strictly verified against the Telegram hash.
- Ensure CORS and Cookie settings are strict (`SameSite=Lax`, `Secure`).

Поздравляю! Директория acme-v02... означает, что сертификат успешно получен, и теперь твой сайт криптографически защищен. 

Теперь переходим к самому вкусному — созданию полноценного веб-приложения (SaaS) вокруг твоего бота.

Так как ты Python-разработчик (раз пишешь на aiogram) и вообще не хочешь лезть в дебри JavaScript-фреймворков (и правильно делаешь!), а дизайн планируешь полностью отдать LLM, тебе нужен максимально простой, монолитный и "LLM-friendly" стек.

Если ты сейчас полезешь в React, Next.js, Webpack и npm, ты сойдешь с ума от количества конфигураций, а когда LLM выдаст код с устаревшими хуками, ты не сможешь это починить.

Вот идеальный стек для тебя (и для ИИ, который будет писать код):

### 1. Бэкенд: FastAPI (Python)
*   Почему: Это современный, сверхбыстрый веб-фреймворк на Python. Он тоже асинхронный (как твой aiogram). 
*   Главная киллер-фича: Твой новый веб-сервер сможет использовать ТУ ЖЕ САМУЮ БАЗУ ДАННЫХ (PostgreSQL) и те же самые ORM-модели (src/db/models.py), что и твой бот! Тебе не нужно придумывать синхронизацию. Сайт просто будет читать из БД то, что записал бот.

### 2. Фронтенд: HTML + Tailwind CSS (через CDN)
*   Почему Tailwind: Это CSS-фреймворк, где стили пишутся прямо в HTML-классах (например, <div class="bg-black text-white p-4 rounded-lg">). 
*   Почему это идеально для LLM: Нейросети (Claude, ChatGPT) генерируют Tailwind-дизайны божественно. Ты просто пишешь промпт: *"Сгенерируй мне темный дашборд в стиле киберпанка/корпорации Monolith с сайдбаром и карточками метрик"*, и она выдает тебе один готовый HTML-файл, который выглядит на миллион долларов. Никаких сборок фронтенда, никаких npm install.

### 3. Графики: Chart.js или ApexCharts
*   LLM отлично умеет писать простенькие JavaScript-вставки внизу HTML-страницы, чтобы нарисовать красивые графики твоей продуктивности, забирая данные по API из твоего FastAPI.

### 4. Авторизация: Telegram Login Widget
Тебе не нужно делать формы регистрации с паролями, email-ами и восстановлением доступа.
У Телеграма есть готовый [Telegram Login Widget](https://core.telegram.org/widgets/login).
Как это работает:
1. LLM вставляет на твой сайт красивую кнопку «Log in with Telegram».
2. Юзер нажимает её (если он с телефона, телеграм сам его авторизует, если с ПК — попросит подтвердить в приложении).
3. Телеграм перекидывает юзера обратно на твой FastAPI-бэкенд и передает скрытые данные: telegram_id, first_name и криптографический hash.
4. Твой FastAPI проверяет этот hash с помощью токена твоего бота. Если хэш совпал — значит, Телеграм ручается, что это именно тот юзер.
5. Бэкенд выдает юзеру сессионную куку (cookie) и пускает в Дашборд.

---

### Как это будет выглядеть архитектурно на твоем сервере

У тебя в папке /opt/pulse-monolith-bot появится новая папка web/ (или отдельный контейнер webapp в docker-compose.yml).

Caddy (твой верный маршрутизатор) будет настроен так:
*   Запросы на pulsemonolith.com/webhook -> идут в bot
*   Запросы на pulsemonolith.com/* (всё остальное) -> идут в webapp (твой FastAPI).

А сам процесс разработки будет выглядеть так:
1. Ты открываешь Claude / ChatGPT.
2. Пишешь: *"Я делаю веб-дашборд на FastAPI + Jinja2 + Tailwind. Напиши мне HTML-шаблон для главной страницы с графиком часов и списком активных проектов. И напиши роут FastAPI, который будет отдавать эти данные из базы"*.
3. Копируешь код в проект. Всё работает.

Твой план действий, если согласен на этот стек:
1. Мы добавим в твой проект FastAPI и библиотеку для рендеринга шаблонов (Jinja2).
2. Настроим Telegram Login Widget, чтобы он связал твоего бота и твой сайт в единую экосистему.
3. Научим твой Caddy перенаправлять трафик на новый веб-сервер.

Готов попробовать FastAPI + Tailwind? Могу расписать первый шаг — как прикрутить виджет логина Телеграма.