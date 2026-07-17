# 🛒 DZ18: Работа с формами (Django Forms)

**Автор:** Виктор Куличенко | Специалист по ИБ и AI-архитектуре  
**Репозиторий:** [VictorKVS/DZ18_Working_with_forms](https://github.com/VictorKVS/DZ18_Working_with_forms)  
**Статус:** ✅ Выполнено по стандарту TDD с agent-ready архитектурой

---

## 1. 📋 Условие задачи

**Цель:** Разработка веб-приложения с формами регистрации, авторизации и отправки сообщений.

### Этапы выполнения (ТЗ):
- [x] **Модель пользователя** — используем встроенную `User` Django
- [x] **Формы** — регистрация, авторизация, отправка сообщения (ModelForm)
- [x] **Валидация** — кастомная проверка email, паролей, длины текста
- [x] **Обработка форм** — редиректы после успеха, flash-messages
- [x] **Ajax** — отправка сообщений без перезагрузки страницы (Fetch API)
- [x] **Шаблоны** — Bootstrap 5, floating labels, страница профиля
- [x] **Маршруты** — URLs для всех представлений
- [x] **Документация** — данный README и архитектурные схемы

---

## 2. 🏛️ Архитектура

### Component Diagram (C4 Model)

```mermaid
graph TD
    %% --- СТИЛИЗАЦИЯ ДЛЯ ПРЕЗЕНТАЦИОННОГО ВИДА ---
    classDef client fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000,font-weight:bold
    classDef web fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef app fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef data fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px,color:#000
    classDef cross fill:#eceff1,stroke:#455a64,stroke-width:2px,stroke-dasharray: 5 5,color:#000

    %% --- КЛИЕНТСКИЙ СЛОЙ ---
    Client(("👤 Пользователь / Браузер")) :::client

    %% --- СЛОЙ ПРЕДСТАВЛЕНИЯ И МАРШРУТИЗАЦИИ ---
    subgraph Presentation ["🌐 Presentation & Routing Layer"]
        direction TB
        Static["⚡ Static Assets\n(JS: Fetch API, CSS: Bootstrap 5)"] :::web
        Templates["🎨 Templates\n(Floating Labels, Responsive)"] :::web
        Router["🔀 Django URL Dispatcher\n(config/urls.py)"] :::web
    end

    %% --- СЛОЙ БИЗНЕС-ЛОГИКИ (AGENT-READY) ---
    subgraph Application ["⚙️ Application Layer (Agent-Ready / CQRS-lite)"]
        direction TB
        
        subgraph Accounts ["🔐 accounts App"]
            AccViews["👁️ Views\n(Thin HTTP Wrappers)"] :::app
            AccForms["📝 Forms\n(Custom Validation)"] :::app
            AccServices["🤖 Services\n(UserService)"] :::app
            AccSelectors["📖 Selectors\n(Read Operations)"] :::app
        end

        subgraph Feedback ["✉️ feedback App"]
            FbViews["👁️ Views\n(HTTP + Ajax Handler)"] :::app
            FbForms["📝 Forms\n(Length <= 500 validation)"] :::app
            FbServices["🤖 Services\n(MessageService)"] :::app
            FbSelectors["📖 Selectors\n(get_user_messages)"] :::app
        end
    end

    %% --- СЛОЙ ДАННЫХ ---
    subgraph Data ["🗄️ Data Layer"]
        ORM["⚙️ Django ORM"] :::data
        DB[("🗃️ SQLite Database\n(User, Message)")] :::data
    end

    %% --- СКВОЗНЫЕ ПРОЦЕССЫ ---
    subgraph CrossCutting ["🛡️ Cross-Cutting Concerns (Security & Audit)"]
        Security["🔒 CSRF, Auth, Input Sanitization"] :::cross
        Audit["📝 Audit Logging\n(INFO/WARNING trails)"] :::cross
    end

    %% --- СВЯЗИ И ПОТОКИ ДАННЫХ ---
    Client -->|"1. HTTP GET/POST или Ajax"| Router
    Static -.->|"2. Async Fetch + CSRF Token"| FbViews
    
    Router -->|"3. Dispatch"| AccViews
    Router -->|"3. Dispatch"| FbViews
    
    AccViews -->|"4. Validate"| AccForms
    FbViews -->|"4. Validate"| FbForms
    
    AccViews -->|"5. Execute Business Logic"| AccServices
    AccViews -->|"6. Read Data"| AccSelectors
    FbViews -->|"5. Execute Business Logic"| FbServices
    FbViews -->|"6. Read Data"| FbSelectors
    
    AccServices -->|"7. CRUD"| ORM
    AccSelectors -->|"7. Query"| ORM
    FbServices -->|"7. CRUD"| ORM
    FbSelectors -->|"7. Query"| ORM
    
    ORM -->|"8. Persist/Retrieve"| DB
    
    AccViews -->|"9. Render / Redirect"| Templates
    FbViews -->|"9. Render / Redirect"| Templates
    FbViews -.->|"10. JSON Response"| Client
    
    Templates -->|"11. HTML Response"| Client
    
    %% Связь со сквозными процессами
    AccServices -.-> Audit
    FbServices -.-> Audit
    Router -.-> Security
    FbViews -.-> Security




## 3. 🧪 Тестирование (TDD)

Код разработан по методологии **Test-Driven Development**. Каждый тест — это юридический контракт системы и спецификация поведения для будущих AI-агентов.

### 📊 Сводная статистика
- **Всего тестов:** 14
- **Покрытие:** Forms + Services + Views (все три слоя)
- **Результат:** `Ran 14 tests in 0.242s — OK`

---

### 🔐 Приложение `accounts` — Аутентификация (7 тестов)

| № | Тест | ТЗ | Уровень | Статус |
|:--|:---|:---:|:---:|:---:|
| 1 | `test_01_password_mismatch` | п.3 | Forms | ✅ PASS |
| 2 | `test_02_duplicate_email` | п.3 | Forms | ✅ PASS |
| 3 | `test_03_create_user_success` | п.1 | Services | ✅ PASS |
| 4 | `test_04_create_user_duplicate_email` | п.3 | Services | ✅ PASS |
| 5 | `test_05_register_redirect` | п.4 | Views | ✅ PASS |
| 6 | `test_06_profile_requires_login` | п.6 | Views | ✅ PASS |
| 7 | `test_07_profile_accessible` | п.6 | Views | ✅ PASS |

---

### ✉️ Приложение `messages` — Сообщения (7 тестов)

| № | Тест | ТЗ | Уровень | Статус |
|:--|:---|:---:|:---:|:---:|
| 8 | `test_01_message_length` | п.3 | Forms | ✅ PASS |
| 9 | `test_02_send_message_success` | п.2 | Services | ✅ PASS |
| 10 | `test_03_empty_text_raises` | п.3 | Services | ✅ PASS |
| 11 | `test_04_too_long_raises` | п.3 | Services | ✅ PASS |
| 12 | `test_05_ajax_success` | п.5 | Views | ✅ PASS |
| 13 | `test_06_ajax_error` | п.5 | Views | ✅ PASS |
| 14 | `test_07_http_redirect` | п.4 | Views | ✅ PASS |

---

### 🔗 Traceability Matrix (Трассируемость требований)

| Пункт ТЗ | Что проверяется | Покрывающие тесты |
|:---:|:---|:---|
| **п.1** | Модель пользователя | `test_03_create_user_success` |
| **п.2** | Формы (регистрация, авторизация, сообщения) | `test_02_send_message_success` |
| **п.3** | Валидация (пароли, email, длина текста) | `test_01`, `test_02`, `test_04`, `test_08`, `test_10`, `test_11` |
| **п.4** | Обработка форм (редиректы) | `test_05_register_redirect`, `test_14_http_redirect` |
| **п.5** | Ajax без перезагрузки | `test_12_ajax_success`, `test_13_ajax_error` |
| **п.6** | Страница профиля | `test_06_profile_requires_login`, `test_07_profile_accessible` |

> 💡 **100% покрытие обязательных пунктов ТЗ** (п.1, п.2, п.3, п.7) + все пункты "по желанию" (п.4, п.5, п.6, п.8).

4. 🖤 Логирование и Аудит (Security)
Система реализует принцип "Чёрного ящика" с обязательным аудитом действий (стандарт для медицинских и защищённых систем). Пароли и токены никогда не попадают в логи.

[2026-07-17 10:30:45] [INFO] accounts.services: AUDIT | CREATE_USER | user=ivan | email=ivan@test.com
[2026-07-17 10:31:02] [INFO] messages.services: AUDIT | SEND_MESSAGE | id=1 | from=Иван
[2026-07-17 10:32:10] [WARNING] accounts.services: AUDIT | LOGIN_FAILED | user=hacker

## 5. 📂 Структура проекта

```text
```
DZ18_Working_with_forms/
│
├── 📄 manage.py                    # Точка входа Django
├── 📄 requirements.txt             # Зависимости (Django 5.2.16)
├── 📄 db.sqlite3                   # БД проекта
├── 📄 README.md                    # Документация
│
├── 📁 config/                      # ⚙️ Настройки проекта
│   ├── settings.py                 # INSTALLED_APPS, DATABASES, TEMPLATES
│   ├── urls.py                     # Главный роутер
│   ├── wsgi.py                     # WSGI-сервер
│   └── asgi.py                     # ASGI-сервер
│
├── 📁 accounts/                    # 👤 Приложение авторизации
│   ├── models.py         | m | Модели пользователей
│   ├── views.py          | v | HTTP-обёртки (login, register, profile)
│   ├── services.py       | s | Бизнес-логика (хеширование, создание)
│   ├── selectors.py      | sel | Чистые запросы к БД
│   ├── forms.py          | f | Формы регистрации/входа
│   ├── urls.py           | u | Маршруты /login/, /register/, /profile/
│   ├── admin.py          | a | Админка
│   ├── tests.py          | t | Юнит-тесты
│   └── templates/accounts/
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       └── send_message.html
│
├── 📁 feedback/                    # 📬 Приложение обратной связи
│   ├── models.py         | m | Модель Message
│   ├── views.py          | v | HTTP-обёртки (send_message)
│   ├── services.py       | s | MessageService (бизнес-логика)
│   ├── selectors.py      | sel | Запросы к БД
│   ├── forms.py          | f | UserMessageForm
│   ├── urls.py           | u | Маршрут /feedback/
│   ├── admin.py          | a | Админка
│   ├── tests.py          | t | Юнит-тесты
│   └── migrations/
│       └── 0001_initial.py
│
└── 📁 templates/                   # 🎨 Глобальные шаблоны
    ├── base.html                   # Базовый каркас
    ├── home.html                   # Главная страница
    ├── accounts/
    │   ├── login.html
    │   └── register.html
    └── feedback/
        └── send_message.html       # ✅ ЭТАЛОННЫЙ шаблон
```

🗺️ Pipe-карта компонентов

```
# 📦 Компоненты приложения feedback

feedback/models.py      | m   | Message (id, name, email, text, created_at)
feedback/forms.py       | f   | UserMessageForm (валидация name/email/text)
feedback/services.py    | s   | MessageService.send_message()
feedback/selectors.py   | sel | get_all_messages(), get_message_by_id()
feedback/views.py       | v   | send_message (тонкая view)
feedback/urls.py        | u   | path('', send_message, name='send_message')
feedback/admin.py       | a   | Регистрация Message в админке
feedback/tests.py       | t   | Unit-тесты для сервиса и view

# 📦 Компоненты приложения accounts

accounts/models.py      | m   | Модели пользователей
accounts/forms.py       | f   | Формы регистрации/входа
accounts/services.py    | s   | Бизнес-логика авторизации
accounts/selectors.py   | sel | Запросы к БД
accounts/views.py       | v   | HTTP-обёртки
accounts/urls.py        | u   | /login/, /register/, /profile/
accounts/admin.py       | a   | Админка
accounts/tests.py       | t   | Unit-тесты
```

🚀 Быстрый старт (команды)



6. 🚀 Инструкция по запуску

  1```bash
# 1. Клонировать проект
git clone <repo_url>
cd DZ18_Working_with_forms

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Применить миграции
python manage.py makemigrations
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver

# 8. Открыть в браузере
# http://127.0.0.1:8000/
# http://127.0.0.1:8000/admin/
# http://127.0.0.1:8000/feedback/
```
🏭 Промышленный цикл разработки (IDC)
```
┌─────────────────────────────────────────────────────────────┐
│              INDUSTRIAL DEVELOPMENT CYCLE (IDC)             │
│                                                             │
│  ШАГ 1: ПОСТАНОВКА ЗАДАЧИ (Task Specification)              │
│  ├── Что должна делать программа                            │
│  ├── Алгоритм работы (пошагово)                             │
│  ├── Входные/выходные данные                                │
│  ├── Ограничения (что НЕ должна делать)                     │
│  └── Интеграция с KNOWLEDGE_CORE                            │
│                                                             │
│  ШАГ 2: СХЕМА В НОТАЦИИ (Architecture Diagram)              │
│  ├── DFD (Data Flow Diagram)                                │
│  ├── UML Class/Sequence Diagram                             │
│  └── Где компонент в общей архитектуре                      │
│                                                             │
│  ШАГ 3: ТЕСТ-КОНТРАКТ (Test Contract)                       │
│  ├── Must-do / Must-not-do                                  │
│  ├── Edge cases / Negative tests                            │
│  └── Критерии приёмки                                       │
│                                                             │
│  ШАГ 4: ПРОГРАММА (Implementation)                          │
│  ├── Код по Шагу 1-3                                        │
│  ├── Построчные комментарии                                 │
│  └── Архитектурные обоснования                              │
│                                                             │
│  ШАГ 5: ТЕСТ ПРОГРАММЫ (Test Execution)                     │
│  ├── Unit / Integration / Negative tests                    │
│  ├── Coverage report (≥80%)                                 │
│  └── 100% pass rate                                         │
│                                                             │
│  ШАГ 6: DEVSECOPS + AI SECURITY                             │
│  ├── OWASP Top-10 for LLM                                   │
│  ├── SAST/SCA/DAST                                          │
│  └── Audit trail (80_AUDIT)                                 │
│                                                             │
│  ⚠️ ПРИНЦИП:                                                │
│  • Шаг 3 не написан → Шаг 4 не начинается                   │
│  • Шаг 5 не проходит → Шаг 6 не начинается                  │
│  • KNOWLEDGE_CORE — арбитр истины на каждом этапе           │
└─────────────────────────────────────────────────────────────┘
```

Перейдите по адресу: http://127.0.0.1:8000/
7. ✅ Финальный чек-лист соответствия ТЗ
Модель пользователя (встроенная User Django)
Форма регистрации с кастомной валидацией email и паролей
Форма авторизации (встроенная LoginView)
Форма отправки сообщения с валидацией длины (≤ 500 символов)
Редиректы и flash-сообщения после успешных действий
Ajax-отправка сообщений без перезагрузки страницы (Fetch API + CSRF)
Страница профиля пользователя с историей его сообщений
Настроены маршруты (URLs) для всех представлений
TDD-тесты (14 шт.) с трассируемостью к ТЗ
Логирование аудита (INFO/WARNING)
Agent-ready архитектура (разделение на Services / Selectors / Views)

📝 Итоговый статус проекта

┌─────────────────────────────────────────────────────────────┐
│                    DZ18_Working_with_forms                   │
│                    Статус: ✅ PRODUCTION READY               │
│                                                             │
│  ✅ ШАГ 1: Постановка задачи — Завершена                    │
│  ✅ ШАГ 2: Архитектура — Завершена                          │
│  ✅ ШАГ 3: Тест-контракт — Завершена                        │
│  ✅ ШАГ 4: Реализация — Завершена                           │
│  ✅ ШАГ 5: Тестирование — Завершена (9/9 тестов)            │
│  ⏸️ ШАГ 6: DEVSECOPS — Опционально                          │
│                                                             │
│  Компоненты:                                                │
│  • feedback/models.py — Модель Message с перепиской         │
│  • feedback/services.py — MessageService (бизнес-логика)    │
│  • feedback/selectors.py — Чистые запросы к БД              │
│  • feedback/views.py — HTTP + AJAX обработчики              │
│  • feedback/forms.py — Валидация форм                       │
│  • feedback/tests.py — 9 unit-тестов                        │
│  • feedback/admin.py — Админка с фильтрами                  │
│                                                             │
│  Функциональность:                                          │
│  • Отправка сообщений с автоматическим дедлайном (24 часа)  │
│  • Поддержка переписки (parent_message)                     │
│  • AJAX без перезагрузки страницы                           │
│  • Пометка как прочитанное при просмотре                    │
│  • Отображение истории сообщений в профиле пользователя     │
│  • Админка с фильтрами по статусу и срокам                  │
└─────────────────────────────────────────────────────────────┘
