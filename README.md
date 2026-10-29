# gatein_back

بک‌اند پروژه Gatein — یک سرویس مبتنی **FastAPI** برای مدیریت ورود و خروج کاربران (Gate-in/attendance system) به همراه احراز هویت OTP، مدیریت سانس‌ها، اهدای جوایز (Gift)، بازخورد کاربران (Feedback) و پیام‌رسانی (Notification).

---

## فهرست مطالب

- [تکنولوژی‌ها و وابستگی‌ها](#تکنولوژی‌ها-و-وابستگی‌ها)
- [ساختار پروژه](#ساختار-پروژه)
- [طراحی معماری](#طراحی-معماری)
- [شیوه کد‌نویسی و قراردادها](#شیوه-کدنویسی-و-قراردادها)
- [اجزا و ماژول‌ها](#اجزا-و-ماژول‌ها)
- [مدل‌های دیتابیس](#مدل‌های-دیتابیس)
- [انواع Enum دیتابیس](#انواع-enum-دیتابیس)
- [رابط‌های API (Routers)](#رابط‌های-api-routers)
- [احراز هویت و مدیریت نشست](#احراز-هویتی-و-مدیریت-نشست)
- [رسانه و فایل‌ها](#رسانه-و-فایل‌ها)
- [پیام‌رسانی و SMS](#پیام‌رسانی-و-sms)
- [Startup / Diagnostics](#startup--diagnostics)
- [راه‌اندازی محلی](#راه‌اندازی-محلی)
- [مهاجرت دیتابیس (Alembic)](#مهاجرت-دیتابیس-alembic)
- [توضیح فایل‌های کمکی](#توضیح-فایل‌های-کمکی)

---

## تکنولوژی‌ها و وابستگی‌ها

| لایه | تکنولوژی | نسخه |
|---|---|---|
| وب فریمورک | **FastAPI** | 0.139.2 |
| ORM | **SQLAlchemy 2.0** (Async) | 2.0.51 |
| اکوسیستم SQLAlchemy | asyncpg / psycopg / psycopg2 | 0.31.0 / 3.3.4 |
| دیتابیس | **PostgreSQL** | 16 |
| کش / نشست | **Redis** (async) | 8.0.1 |
| توکن / JWT | **PyJWT** + **python-jose** | 2.13.0 / 3.5.0 |
| مدیریت پیکربندی | **pydantic-settings** | 2.14.2 |
| واسط SMS | **Kavenegar** | 1.1.2 |
| کلاینت Keycloak | **keycloak** | 3.1.5 |
| سرور | **Uvicorn** (dev) / **Gunicorn + UvicornWorker** (prod) | 0.51.0 |
| استاتوس کوادی | مالتی‌پرداز core | multiprocessing |

---

## ساختار پروژه

```
gatein_back/
├── app/
│   ├── main.py                     # نقطه ورود اصلی (uvicorn / gunicorn)
│   ├── .env                        # متغیرهای محیطی (رمزهای سری، اتصال به دیتابیس)
│   ├── backbone/
│   │   ├── configs.py              # کلاس Configs (pydantic-settings) — تمام تنظیمات
│   │   ├── exceptions.py           # همه Exception های سفارشی + Errhandler
│   │   ├── locator_service.py      # DI Container سفارشی (LocatorService)
│   │   ├── db/
│   │   │   ├── sqlalchemy_db_based.py   # TableMixin, SQLAlchemyAdapter, EnumMixin
│   │   │   ├── tables.py               # مدل‌های SQLAlchemy (User, Slot, …)
│   │   │   └── db_enums.py           # کلاس‌های Enum table-based
│   │   ├── db_enums_generated.py    # enum های تولیدشده از دیتابیس (auto-gen)
│   │   ├── adapters/
│   │   │   ├── async_auth_adapter.py     # JWT, OTP, Session, Token Rotation
│   │   │   ├── async_redis_adapter.py    # Redis client wrapper (pickle-based)
│   │   │   ├── file_storage_service.py   # ذخیره فایل محلی روی disk
│   │   │   └── sms_adapter_kavenegar.py  # واسط SMS Kavenegar
│   │   ├── bases/
│   │   │   └── base_request.py  # BaseRequest / BaseResponse
│   │   ├── mixins/
│   │   │   └── pydantic.py      # PydanticMixin ها (phone, token, pagination, …)
│   │   ├── middlewares/
│   │   │   ├── auth_middleware.py           # اعتبارسنجی Bearer token از Redis
│   │   │   ├── header_time_middleware.py    # ثبت X-Process-Time + timing log
│   │   │   └── logger_middelware.py         # لاگ کامل request/response
│   │   ├── helpers/
│   │   │   └── more_funcs.py     # get_current_user_id(request)
│   │   ├── text_app/
│   │   │   ├── en.json / fa.json # متن‌های چندزبانه
│   │   │   └── text_app.py       # TextApp.get(key, lang=…)
│   │   └── scripts/
│   │       ├── fill_userid.py    # اسکریپت پرکردن فیلدهای خالی
│   │       └── enum_sync.py      # اسکریپت همگام‌سازی دستی enum ها
│   ├── bootstrap/
│   │   └── locator.py     # راه‌اندازی singleton ها (DB, Redis, Auth, SMS, Storage)
│   └── routers/
│       ├── auth.py         # POST /auth/otp, /auth/verify_otp, /auth/refresh
│       ├── user.py         # GET/PUT /users/me, settings, permissions, sessions
│       ├── gift.py         # GET /user/gifts (history)
│       ├── feedback.py     # GET/POST /user/feedbacks
│       ├── notification.py # GET/PATCH /user/notifications
│       └── progress_log.py # GET/POST /user/progress-logs
├── alembic/
│   ├── versions/        # اسکرپت‌های مهاجرت دیتابیس (alembic)
│   ├── env.py
│   └── script.py.mako
├── docker-compose.yml   # PostgreSQL 16 + Redis 7
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## طراحی معماری

### 1. Dependency Injection — LocatorService

به جای استفاده از FastAPI Depends، پروژه از یک **میکرو IoC container** به نام `LocatorService` استفاده می‌کند:

```python
loc = LocatorService()

# Eager Singleton (ساخت هنگام startup)
loc.registerSingleton("Configs", lambda: cfg)
await loc.registerSingletonAsync("AsyncRedisAdapter", ...)
loc.registerSingleton("SQLAlchemyAdapter", ...)

# دریافت سرویس
sqlalchemy: SQLAlchemyAdapter = loc.get("SQL SQLAlchemyAdapter")
```

**چرا؟**
- کنترل کامل بر lifetime شیء (Singleton vs Factory)
- امکان استفاده در اسکریپت‌های غیر FastAPI
- کاهش وابستگی به mechanism داخلی FastAPI

### 2. Mixin-Based Table Design

تمام مدل‌های SQLAlchemy از `TableMixin` ارث‌بری می‌کنند که فیلدهای مشترک را اضافه می‌کند:

| Mixin | فیلدها |
|---|---|
| `IdMixin` | `id` — sequence از 10000، auto-increment |
| `TimestampMixin` | `created_at`, `updated_at` (timezone-aware) |
| `SoftDeleteMixin` | `is_deleted`, `deleted_at` |
| `UserAuditMixin` | `created_by_id`, `updated_by_id` (FK به users) |
| `UtilityMixin` | `__repr__`, `to_dict()` |

نتیجه: هر جدول حداقل این فیلدها را دارد بدون نیاز به تکرار کد.

### 3. Enum Tables (بدون ENUM پایگاه داده)

به جای استفاده از PostgreSQL `ENUM` type، پروژه از **جدول‌های پایه** (مثل `theme_type_enum`, `slot_role_enum`) استفاده می‌کند. مزایا:
- امکان ویرایش enum values بدون migration
- soft-delete روی آیتم‌ها
- sync خودکار با `EnumMixin.sync_all_enums()` هنگام startup
- تولید فایل Python (`db_enums_generated.py`) از روی داده‌های واقعی

### 4. Auth Flow (OTP + JWT + Redis Sessions)

```
[Client]
   │ POST /auth/otp   (phone)
   ▼
[OTP Generator] ──► Redis key: "otp:{user_id}"  (TTL 120s)
   │
   ▼ (send SMS —现阶段 کامنت شده)
[Client]
   │ POST /auth/verify_otp  (phone + code)
   ▼
[Verify OTP] ──► delete OTP key
   │
   ▼
[Create Tokens] ──► JWT access (1 day) + refresh (15 days)
   │
   ▼
[Save Session] ──► Redis key: "session:{sid}" + "user_sessions:{uid}" (set)
   │
   ▼
[Response] ──► { user_id, phone, access_token, refresh_token, ... }
```

**Token Rotation:** هنگام refresh، session قدیمی حذف شده و session جدید ساخته می‌شود.

### 5. Middleware Stack

```
Request → [RequestResponseLoggerMiddleware]
        → [HeaderTimeMiddleware]
        → [AuthMiddleware]          (skip public routes)
        → Router Handler
        → Response → (headers set, body consumed for logging)
```

---

## شیوه کدنویسی و قراردادها

### سبک نام‌گذاری
- **متغیرها/تابع‌ها:** snake_case (همخوان با PEP 8)
- **کلاس‌ها:** PascalCase
- **رشته‌ها:** انگلیسی (comments گاهی فارسی)
- **پروژه ریشه:** `app/` در دایرکتوری root (sys.path تنظیم شده)

### Request / Response Pattern
هر endpoint از این الگو پیروی می‌کند:
1. دریافت سرویس‌ها از `loc.get(...)`
2. استخراج `user_id = get_current_user_id(request)`
3. باز کردن transaction/session از adapter
4. اجرا و return مدل Pydantic

```python
@router.get("/me", response_model=UserMeResponse)
async def get_me(request: Request):
    sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
    user_id = get_current_user_id(request)

    async with sqlAlchemyAdapter.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise Exception404()
        return UserMeResponse(user_id=user.id, ...)
```

### استثناء‌ها (Exceptions)
همه exception ها از `BaseHttpException` ارث‌بری کرده و در `Errhandler` یکجا هندل می‌شوند:
- `Exception400` / `Exception404` / `Exception401MissingToken` / `Exception401ExpiredToken` / `Exception400OTPExpired` / ...

ورودی خطاهای 422 و خطاهای عمومی توسط `Errhandler.validation_error` و `Errhandler.general_error` به JSON پاسخ تبدیل می‌شوند.

### Multiple Inheritance در Pydantic Models
برای جلوگیری از تکرار فیلدهای مشترک، از multiple inheritance استفاده می‌شود:

```python
class VerifyOTPResponse(
    BaseResponse,
    PydanticMixinUserID,
    PydanticMixinContact,
    PydanticMixinTokenRequired,
):
    name: str | None = ...
```

### Pagination
همه لیست‌ها (gifts, feedbacks, notifications, progress_logs) از `PydanticMixinPagination` استفاده می‌کنند (`limit` و `offset`) و `total` جداگانه شمارش می‌شود.

### Async/Await
تمام عملیات DB و Redis به صورت async هستند. در locator، سرویس‌های async با `await loc.registerSingletonAsync(...)` تزریق می‌شوند.

---

## اجزا و ماژول‌ها

### `configs.py` — پایگاه تنظیمات
تنظیمات از `.env` خوانده می‌شود (pydantic-settings). مقدار پیش‌فرض:
- `DEBUG=True`
- `POSTGRES_HOST=localhost`
- `REDIS_HOST=localhost`
- `OTP_LENGTH=6`, `OTP_EXPIRE_MINUTES=5`
- `TOKEN_EXPIRE_MINUTES=28800` (20 روز), `REFRESH_TOKEN_EXPIRE_MINUTES=57600` (40 روز)
- `TORTOISE_ORM` (نمونه باقیمانده از گذشته، فعلاً استفاده نمی‌شود)

### `exceptions.py` — مدیریت خطا
یک مجموعه کامل exception از 4xx تا 5xx شامل:
- `Exception400OTPExpired` — OTP منقضی شده
- `Exception404OTPNotRequested` — کاربر OTP درخواست نداده
- `Exception503SMS` — سرویس SMS از کار افتاده
- `Errhandler.general_error` — شامل استخراج `orig.args[0]` از خطاهای SQLAlchemy

### `locator_service.py` — DI Container
پشتیبانی از ۴ حالت ثبت:
1. `registerSingleton` — eager sync
2. `registerSingletonAsync` — eager async
3. `registerSingletonLazy` — lazy sync
4. `registerFactory` — factory (هر بار نمونه جدید)

### `text_app/` — چندزبانگی
دو فایل JSON (`en.json`, `fa.json`) و کلاس `TextApp.get(key, lang=Language.EN)` با پشتیبانی از قالب‌بندی positional و keyword.

### `file_storage_service.py` — ذخیره فایل محلی
ذخیره فایل‌ها در پوشه `storage/` با نام UUID. URL خروجی: `/files/{folder}/{uuid}.ext`. Mount شده در `StaticFiles`.

### `async_redis_adapter.py` — Redis Wrapper
پشتیبانی از serialization با `pickle` (برای داده‌های Python-native). دارای background snapshot (BGSAVE) هر 5 ثانیه.

---

## مدل‌های دیتابیس

### جدول `users`
فیلدها: `name`, `given_name`, `email` (unique), `phone` (unique, index), `birthday`, `is_profile_completed`, `profile_image`

ارتباطات:
- `settings` (1:1)
- `slots` (1:N)
- `attendance` (1:N)
- `work` (1:N)
- `gifts` (1:N)
- `sent_feedbacks` / `received_feedbacks` (1:N)
- `sent_notifications` / `notification_recipients` (1:N)
- `progress_logs` (1:N)

### جدول `user_permissions` (junction)
junction table بین `users` و `permissions_enum`.

### جدول `user_settings`
`theme_id`, `language_id`, `enable_notifications`, `extra_settings` (JSON).

### جدول `user_progress_logs`
`metric_type_enum_id` (FK), `value` (float), `notes` (text).

### جدول `slots`
`schedules` (1:N), `title`, `capacity`, `slot_type_id` (FK), `memberships` (1:N), `gates` (M:N via `slot_gate`), `attendance` (1:N).

### جدول `slot_schedules`
`slot_id`, `schedules_type_id` (schedule recurrence), `date`, `day_number`, `monthly_relative_week`, `start_time`, `end_time`, `valid_from_date`, `valid_until_date`.

### جدول `slot_memberships` (junction)
`slot_id`, `user_id`, `role_enum_id` — سه‌تایی primary key.

### جدول `gates`
`name`, `code` (UUID, unique), `is_active`.

### جدول `slot_attendances`
`slot_id`, `user_id`, `gate_id`, `attendance_date`, `check_in_time`, `check_out_time`.

### جدول `works` و `work_schedules`
مشابه slots اما برای work/شغل.

### جدول `gifts` و `user_gifts`
`gifts`: `title`, `description`, `value`, `is_active`, `valid_from`, `valid_until`.
`user_gifts`: `user_id`, `gift_id`, `is_gifted`, `gifted_at`.

### جدول `user_feedbacks`
`recipient_id`, `sender_id`, `is_anonymous`, `title`, `content`.

### جدول `notifications` و `notification_recipients`
`notifications`: `sender_id`, `title`, `content`.
`notification_recipients`: `notification_id`, `recipient_id`, `is_read`, `read_at`.

---

## انواع Enum دیتابیس

| جدول | مقادیر |
|---|---|
| `theme_type_enum` | DARK, LIGHT, SYSTEM |
| `language_type_enum` | FA, EN, AR |
| `user_metric_type_enum` | WEIGHT, HEIGHT, ENVIRONMENT_SATISFACTION, WORK_INTEREST, BURNOUT_LEVEL, MOTIVATION_SCORE, TEAM_COLLABORATION |
| `permissions_enum` | SYS_REBOOT, USERS_CREATE, USERS_READ, USERS_UPDATE, USERS_DELETE, BILLING_ISSUE_REFUND, ... (20+) |
| `slot_type_enum` | PUBLIC, PRIVATE, ORGANIZATIONAL, EVENT |
| `schedule_recurrence_enum` | ONETIME, WEEKLY, MONTHLY, MONTHLY_RELATIVE |
| `slot_role_enum` | MEMBER, HOST, PRODUCER, ORGANIZER, MANAGER, INSTRUCTOR, COACH, SPEAKER, SECURITY, ... (18+ نقش) |

فایل `db_enums_generated.py` خودکار از روی دیتابیس تولید می‌شود.

---

## رابط‌های API (Routers)

### `/auth` — Authentication (public)

| متد | مسیر | توضیح |
|---|---|---|
| POST | `/auth/otp` | تولید و ارسال OTP به شماره موبایل |
| POST | `/auth/verify_otp` | بررسی OTP، بازگرداندن توکن‌ها + اطلاعات کاربر |
| POST | `/auth/refresh` | رفرش access token با refresh token (token rotation) |

### `/users` — User Management

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/users/me` | پروفایل کاربر جاری |
| PUT | `/users/me` | ویرایش پروفایل (نام، ایمیل، تولد، تصویر) |
| GET | `/users/settings` | تنظیمات (تم، زبان، نوتیفیکیشن) |
| PATCH | `/users/settings` | بروزرسانی تنظیمات |
| GET | `/users/permissions` | لیست دسترسی‌های کاربر |
| GET | `/users/sessions` | لیست نشست‌های فعال |
| DELETE | `/users/sessions/{session_id}` | ابطال یک نشست |
| DELETE | `/users/sessions` | خروج از تمام دستگاه‌ها |
| POST | `/users/logout` | خروج از نشست جاری |

### `/user/gifts` — Gift History

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/user/gifts` | لیست گیفت‌های دریافتی (paginated) |

### `/user/feedbacks` — Feedback

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/user/feedbacks/received` | بازخوردهای دریافتی |
| GET | `/user/feedbacks/sent` | بازخوردهای ارسالی |
| POST | `/user/feedbacks` | ارسال بازخورد جدید |

### `/user/notifications` — Notification

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/user/notifications` | لیست نوتیفیکیشن‌ها (paginated) |
| GET | `/user/notifications/unread-count` | تعداد خوانده‌نشده‌ها |
| PATCH | `/user/notifications/{id}/read` | خوانده‌شدن یک نوتیفیکیشن |
| PATCH | `/user/notifications/read-all` | خوانده‌شدن همه |

### `/user/progress-logs` — Progress Tracking

| متد | مسیر | توضیح |
|---|---|---|
| GET | `/user/progress-logs` | لیست لاگ‌های پیشرفت (paginated، فیلتر metric_type) |
| POST | `/user/progress-logs` | ثبت لاگ جدید |

---

## احراز هویت و مدیریت نشست

### AuthMiddleware
تمام routeها به جز prefixهای زیر نیاز به Bearer token دارند:
- `/auth/` (عمومی)
- `/docs` (Sandbox Swagger)
- `/files` (static files)

token از هدر `Authorization: Bearer <jwt>` خوانده شده و به `request.state.user` و `request.state.token` ست می‌شود.

### Session Data Structure (Redis)
```
Key:    session:{session_id}
Value:  JSON {user_id, session_id, created_at, device_metadata, access_token, refresh_token}
TTL:    refresh_token_ttl (15 روز)

Key:    user_sessions:{user_id}
Type:   Set of session_ids
TTL:    بدون TTL (مدیریت دستی)
```

### Token Rotation
هنگام refresh:
1. validate refresh token
2. حذف session قدیمی
3. ساخت session جدید
4. بازگرداندن access_token و refresh_token جدید

---

## رسانه و فایل‌ها

فایل‌های آپلود شده (پروفایل و ...) در پوشه `storage/` ذخیره می‌شوند:
- `storage/profiles/<uuid>.jpg`
- URL قابل دسترس: `http://host/files/profiles/<uuid>.jpg`

`FileStorageService` متدهای `save()`, `delete()`, `exists()`, `get_path()` را ارائه می‌دهد.

---

## پیام‌رسانی و SMS

واسط SMS با کتابخانه `kavenegar` پیاده شده (`SMSAdapter`). در حال حاضر در flow OTP کامنت شده است (فقط تولید OTP در Redis). ارسال واقعی پیامک در `sms_adapter_kavenegar.py` قابل فعال‌سازی است.

---

## Startup / Diagnostics

### `bootstrap/locator.py` — lifecycle
هنگام شروع FastAPI (lifespan):
1. ثبت `Configs`
2. اتصال Redis (`AsyncRedisAdapter`)
3. ساخت `AsyncRedisAuthAdapter` (با secret hardcoded — باید از env خوانده شود)
4. اتصال PostgreSQL (`SQLAlchemyAdapter`)
5. اجرای `enums_sync()` (همگام‌سازی enum ها + تولید Python enum)
6. ثبت `SMSAdapter` و `FileStorageService`

هنگام توقف: `dispose()` روی SQLAlchemyAdapter.

### `scripts/`
- `fill_userid.py` — اسکرپت تکمیل فیلدهای خالی ID در رکوردهای موجود
- `enum_sync.py` — اجرای دستی همگام‌سازی enum ها

---

## راه‌اندازی محلی

### 1. پیش‌نیازها
- Python 3.11+
- PostgreSQL 16 (یا Docker)
- Redis 7 (یا Docker)

### 2. نصب
```bash
pip install -r requirements.txt
```

### 3. پیکربندی (.env)
```env
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=postgres
REDIS_HOST=localhost
SECRET_KEY=your-secret-key-here
KAVENEGAR_ACCESS_KEY=
KAVENEGAR_SENDER=
```

### 4. اجرای سرویس‌ها با Docker
```bash
docker compose up -d
```

### 5. مهاجرت دیتابیس
```bash
alembic upgrade head
```

### 6. اجرای توسعه
```bash
python -m app.main
# یا
uvicorn bootstrap.api:app --host 0.0.0.0 --port 8001
```

### 7. اجرای تولید
```bash
gunicorn bootstrap.api:app -w 5 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

---

## مهاجرت دیتابیس (Alembic)

مهاجرت‌ها در `alembic/versions/` ذخیره می‌شوند. فایل `alembic.ini` روی `postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/db_app` تنظیم شده.

**مهاجرت‌های موجود:**
- `206dd53333e3_initial_migration.py` — ساخت جدول‌های پایه
- `f16c113363b1_add_sequence.py` — تعریف sequence برای IDs (شروع 10000)
- `fd447f5ddbbb_id_five_digint.py` — تغییر طول ID
- `7d07d652d00b_add_profile_completion_status.py` — افزودن `is_profile_completed`
- `5c1937fd6bd5_user_permission_errors.py` — اصلاح user_permissions
- `9a427d302bca_remove_enum_in_name_user_permission.py` — رفع مشکل enum
- `1d6f220f5c36_fix_bug_errors.py` — رفع باگ
- `6215a39516c7_fix_bug_errors.py`, `703bdc78f2be_fix_bug_errors.py`, `79124bbccfb3_fix_bug_errors.py`, `a35f5ecf8cf6_fix_bug_errors.py`, `e6584c099b8a_fix_bug_errors.py` — رفع باگ‌های متعدد

---

## توضیح فایل‌های کمکی

| فایل | توضیح |
|---|---|
| `mypy.ini` | تنظیمات type-checker mypy |
| `pyrightconfig.json` | تنظیمات type-checker pyright |
| `.flake8` / `.pep8` / `.isort.cfg` / `.pylintrc` | قواعد lint و format |
| `pyproject.toml` | تنظیمات ruff + aerich (ORM) |
| `docker-compose.yml` | سرویس‌های postgres:16 و redis:7 |
| `requirements.txt` | لیست کامل وابستگی‌ها |

---

## فلسفه طراحی

1. **سادگی در DI:** به جای FastAPI Depends، از LocatorService استفاده شده تا کنترل بیشتری بر lifetime شیءها داشته باشیم و بتوانیم در اسکریپت‌های خارج از فریمورک نیز از آن‌ها استفاده کنیم.

2. **Mixin-Based Architecture:** فیلدهای مشترک هر جدول (id, created_at, soft-delete, user audit) در mixin‌ها تعریف شده و در هر مدل به صورت Composition استفاده می‌شود. این کار از تکرار کد جلوگیری می‌کند.

3. **Enum Table به جای DB ENUM:** به جای استفاده از نوع enum دیتابیس PostgreSQL، از جدول‌های معمولی استفاده شده تا امکان تغییر، اضافه و soft-delete مقادیر بدون migration فراهم باشد.

4. **OTP بدون SMS (现阶段):** سیستم OTP با Redis پیاده‌سازی شده ولی ارسال SMS در حال حاضر غیرفعال است (کامنت شده). این به معنی تست‌پذیری آسان‌تر و عدم وابستگی خارجی موقت است.

5. **Token Rotation:** هر بار که refresh token استفاده می‌شود، session قبلی ابطال شده و session جدید ساخته می‌شود — این کار از replay attack جلوگیری می‌کند.

6. **لاگ‌نویسی کامل:** middleware Logger تمام request/response را با رنگ ANSI در کنسول چاپ می‌کند تا دیباگ سریع‌تر باشد.
