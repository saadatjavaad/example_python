# دستورالعمل توسعه پروژه FastAPI

این سند به‌عنوان **راهنمای کلی** برای هر پروژه پایتونی مبتنی بر FastAPI نوشته شده است. مفاهیم، ساختار پوشه‌ها، شیوه کد‌نویسی و جایگاه هر جزء در معماری را توضیح می‌دهد.

---

## فهرست

- [۱. معماری کلی](#۱-معماری-کلی)
- [۲. ساختار پوشه‌ها](#۲-ساختار-پوشه‌ها)
- [۳. جایگاه هر مفهوم (Architecture Placement)](#۳-جایگاه-هر-مفهوم-architecture-placement)
- [۴. شیوه کد‌نویسی و قراردادها](#۴-شیوه-کدنویسی-و-قراردادها)
- [۵. لایه‌های اصلی](#۵-لایه‌های-اصلی)
- [۶. مدیریت خطا](#۶-مدیریت-خطا)
- [۷. تست و کیفیت کد](#۷-تست-و-کیفیت-کد)
- [۸. استقرار (Deploy)](#۸-استقرار-deploy)

---

## ۱. معماری کلی

پروژه باید به چند لایهٔ مستقل تقسیم شود تا هر لایه تنها مسئولیت خودش را بداند:

```
+---------------------------+
|         Routers           |  ← ورودی API — فقط HTTP را مدیریت می‌کند
+---------------------------+
            ↓
+---------------------------+
|     Services / Logic      |  ← منطق کسب‌وکار (Business Logic)
+---------------------------+
            ↓
+---------------------------+
|       Adapters            |  ← ارتباط با بیرون (DB, Redis, SMS, S3, …)
+---------------------------+
            ↓
+---------------------------+
|       Data Models         |  ← مدل‌های ORM و DTO
+---------------------------+
```

### اصل کلیدی: سادگی معماری

- هر لایه فقط با لایهٔ پایین‌تر خودش ارتباط مستقیم دارد.
- از import چرخه‌ای (circular import) پرهیز کنید.
- هر فایل باید **یک مسئولیت واحد** داشته باشد.
- از `LocatorService` (یا هر DI container مشابه) برای تزریق وابستگی‌ها استفاده کنید، نه `Depends` ی بیش‌ازحد پیچیده.

---

## ۲. ساختار پوشه‌ها

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                    # نقطهٔ ورود برنامه (uvicorn / gunicorn)
│   ├── .env                       # متغیرهای محیطی (هرگز commit نکنید)
│   │
│   ├── backbone/                  # هستهٔ مشترک پروژه
│   │   ├── configs.py             # تنظیمات برنامه (pydantic-settings)
│   │   ├── exceptions.py          # تعریف exception‌های سفارشی
│   │   ├── locator_service.py     # DI Container سفارشی (IOC)
│   │   ├── constanse.py           # مقادیر ثابت سراسری
│   │   │
│   │   ├── adapters/              # واسط‌های ارتباط با بیرون
│   │   │   ├── async_redis_adapter.py
│   │   │   ├── async_auth_adapter.py
│   │   │   ├── file_storage_service.py
│   │   │   ├── sms_adapter_kavenegar.py
│   │   │   └── keycloak_adapter.py
│   │   │
│   │   ├── bases/                 # کلاس‌های پایه
│   │   │   └── base_request.py    # BaseRequest / BaseResponse
│   │   │
│   │   ├── db/                    # لایهٔ داده
│   │   │   ├── sqlalchemy_db_based.py  # TableMixin, EnumMixin, Adapter
│   │   │   ├── tables.py               # مدل‌های SQLAlchemy
│   │   │   ├── db_enums.py             # تعریف enum table-based
│   │   │   └── db_enums_generated.py   # (auto-generated)
│   │   │
│   │   ├── mixins/                # Mixin های بازمصرف
│   │   │   └── pydantic.py        # PydanticMixin ها
│   │   │
│   │   ├── middlewares/           # middleware های سفارشی
│   │   │   ├── auth_middleware.py
│   │   │   ├── header_time_middleware.py
│   │   │   └── logger_middelware.py
│   │   │
│   │   ├── helpers/               # توابع کمکی عمومی
│   │   │   └── more_funcs.py
│   │   │
│   │   ├── scripts/               # اسکریپت‌های مدیریتی
│   │   │   ├── fill_userid.py
│   │   │   └── enum_sync.py
│   │   │
│   │   └── text_app/              # چندزبانگی
│   │       ├── en.json
│   │       ├── fa.json
│   │       └── text_app.py
│   │
│   ├── bootstrap/                 # راه‌اندازی و lifecycle
│   │   └── locator.py             # register سرویس‌ها + setup/close
│   │
│   └── routers/                   # endpoint های API
│       ├── __init__.py
│       ├── auth.py
│       ├── user.py
│       ├── gift.py
│       ├── feedback.py
│       ├── notification.py
│       └── progress_log.py
│
├── alembic/                       # مهاجرت دیتابیس
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── data/                          # داده‌های محلی (پشتیبان‌گیری)
│
├── storage/                       # فایل‌های آپلود شده (StaticFiles)
│
├── docker-compose.yml             # سرویس‌های جانبی (postgres, redis, …)
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── pyrightconfig.json
├── .flake8
├── .pep8
├── .isort.cfg
├── .pylintrc
└── README.md
```

---

## ۳. جایگاه هر مفهوم (Architecture Placement)

| مفهوم | پوشهٔ مقصد | توضیح |
|---|---|---|
| تنظیمات (Config) | `backbone/configs.py` | کلاس `BaseSettings` از pydantic |
| تعریف Exception | `backbone/exceptions.py` | همه exception ها یکجا |
| DI Container | `backbone/locator_service.py` | LocatorService سفارشی |
| اتصال به دیتابیس | `backbone/db/sqlalchemy_db_based.py` | SQLAlchemyAdapter |
| مدل‌های ORM | `backbone/db/tables.py` | کلاس‌های SQLAlchemy |
| Enum های جدولی | `backbone/db/db_enums.py` | تعریف + sync |
| Enum تولیدشده | `backbone/db_enums_generated.py` | **(auto-generated)** هرگز دستی ویرایش نشود |
| واسط Redis | `backbone/adapters/async_redis_adapter.py` | wrapper کلی |
| واسط احراز هویت | `backbone/adapters/async_auth_adapter.py` | JWT, OTP, Session |
| واسط SMS | `backbone/adapters/sms_adapter_kavenegar.py` | Kavenegar یا هر سرویس دیگر |
| واسط فایل | `backbone/adapters/file_storage_service.py` | ذخیره محلی / S3 |
| واسط Keycloak | `backbone/adapters/keycloak_adapter.py` | OAuth/OIDC |
| کلاس‌های پایه Request | `backbone/bases/base_request.py` | BaseRequest / BaseResponse |
| Mixin های Pydantic | `backbone/mixins/pydantic.py` | Pagination, Phone, Token, … |
| Middleware | `backbone/middlewares/` | هر middleware در فایل جدا |
| توابع کمکی | `backbone/helpers/` | توابع stateless عمومی |
| متن چندزبانه | `backbone/text_app/` | JSON های locale |
| اسکریپت‌های مدیریتی | `backbone/scripts/` | migration helpers, data fillers |
| راه‌اندازی اپلیکیشن | `bootstrap/locator.py` | setup() و close() |
| نقطه ورود | `app/main.py` | uvicorn / gunicorn |
| Endpointها | `routers/` | هر router در فایل جدا |

### قانون کلی: هر فایل باید تنها یک وظیفه داشته باشد

- یک فایل شامل یک mixin باشد، نه سه mixin.
- یک فایل شامل یک adapter باشد، نه چند adapter.
- اگر فایلی بیش از ۳۰۰ خط شد، شکلی از تفکیک مورد نیاز است.

---

## ۴. شیوه کد‌نویسی و قراردادها

### نام‌گذاری

| نوع | سبک | مثال |
|---|---|---|
| متغیرها / توابع | `snake_case` | `get_current_user_id` |
| کلاس‌ها | `PascalCase` | `AsyncRedisAuthAdapter` |
| ثابت‌ها | `UPPER_SNAKE_CASE` | `PUBLIC_PATH_PREFIXES` |
| ماژول‌ها | `snake_case` | `auth_middleware.py` |
| پوشه‌ها | `snake_case` | `backbone/` |

### انکدینگ
- تمام فایل‌ها با **UTF-8** ذخیره شوند.
- هیچ خطی نباید BOM داشته باشد.

### Type Hints
- از `from __future__ import annotations` استفاده **نکنید** (با Pydantic v2 تداخل دارد).
- از `str | None` به جای `Optional[str]` استفاده کنید (Python 3.10+).
- برای فیلدهای Pydantic حتماً `Field(...)` بنویسید.

### Imports
- واردات از `app/` انجام می‌شود، نه path مطلق.
- ترتیب imports:
  1. استاندارد لایبرری
  2. کتابخانه‌های第三方
  3. imports داخلی (`backbone.*`, `bootstrap.*`, `routers.*`)

### سبک async/await
- تمام عملیات IO باید `async` باشد.
- هیچ `time.sleep()` در کد async نداشته باشید — از `asyncio.sleep()` استفاده کنید.
- همواره از `async with` برای مدیریت session/transaction استفاده کنید.

### سبک Pydantic Mixin
به جای تکرار فیلدهای مشترک، از multiple inheritance استفاده کنید:

```python
class SomeResponse(BaseResponse, PydanticMixinUserID, PydanticMixinContact):
    custom_field: str | None = Field(None, description="...")
```

### سبک لایهٔ Router
هر handler باید الگوی زیر را دنبال کند:

```python
@router.get("/path", response_model=ResponseModel)
async def handler(request: Request):
    # 1. دریافت سرویس‌ها از locator
    adapter: ServiceType = loc.get("ServiceName")

    # 2. استخراج context (user_id و ...)
    context_id = get_current_user_id(request)

    # 3. اجرا با transaction/session
    async with adapter.transaction() as session:
        # عملیات DB
        ...

    # 4. بازگرداندن response model
    return ResponseModel(...)
```

### سبک Enum Table
- تعریف enum ها در `db/db_enums.py`.
- هر subclass باید `get_enum_map()` را پیاده کند.
- فایل `db_enums_generated.py` خودکار تولید می‌شود — **هرگز دستی ویرایش نکنید**.

---

## ۵. لایه‌های اصلی

### 5.1 لایهٔ Router (`routers/`)

مسئولیت:
- دریافت درخواست HTTP
- اعتبارسنجی ورودی (Pydantic مدل)
- فراخوانی سرویس‌ها
- بازگرداندن پاسخ

نباید:
- منطق کسب‌وکار پیاده کند
- مستقیماً به دیتابیس وصل شود
- کد auth بنویسد (middleware این کار را می‌کند)

### 5.2 لایهٔ Adapater (`backbone/adapters/`)

مسئولیت:
- پنهان‌سازی جزئیات ارتباط با سرویس‌های خارجی
- تبدیل شکل داده‌های ورودی/خروجی سرویس خارجی به شکل داخلی پروژه

قواعد:
- هر adapter در فایل جداگانه باشد.
- اسم فایل باید با `_adapter` یا `_service` ختم شود.
- تمام متدها باید `async` باشند.

### 5.3 لایهٔ داده (`backbone/db/`)

مسئولیت:
- تعریف مدل‌های SQLAlchemy
- مدیریت اتصالات و transaction ها
- همگام‌سازی enum ها

#### TableMixin — فیلدهای مشترک همهٔ جداول

هر مدل باید از `TableMixin` ارث‌بری کند. این mixin شامل:

| فیلد | نوع | توضیح |
|---|---|---|
| `id` | `int` | primary key، sequence از 10000 |
| `created_at` | `datetime(tz)` | زمان ایجاد |
| `updated_at` | `datetime(tz)` | زمان آخرین ویرایش |
| `is_deleted` | `bool` | soft delete |
| `deleted_at` | `datetime(tz)` | زمان حذف |
| `created_by_id` | `int \| None` | FK به users |
| `updated_by_id` | `int \| None` | FK به users |

اگر فیلدی جدید به `TableMixin` اضافه کنید، **تمام** جداول به‌طور خودکار آن را به ارث می‌برند.

#### EnumMixin — فیلدهای مشترک جداول enum

| فیلد | نوع | توضیح |
|---|---|---|
| `title` | `str` | نام کلیدی (اینگیلیسی) |
| `value` | `str` | مقدار ذخیره‌شده |

همچنین متدهای `sync_enum()` و `sync_all_enums()` برای همگام‌سازی خودکار با دیتابیس.

### 5.4 لایهٔ مدیریت خطا (`backbone/exceptions.py`)

همه exception ها از `BaseHttpException` ارث‌بری می‌کنند. ساختار پاسخ خطا:

```json
{
  "status": "error",
  "message": "توضیح خطا"
}
```

برای validation error:
```json
{
  "status": "error",
  "errors": [
    { "field": "phone", "message": "...", "type": "value_error" }
  ]
}
```

### 5.5 لایهٔ middleware (`backbone/middlewares/`)

هر middleware در فایل جداگانه و با سبک `ClassName(BaseHTTPMiddleware)`:

```python
class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # before
        response = await call_next(request)
        # after
        return response
```

ترتیب middleware در `bootstrap/api.py` مهم است:
```
Request → LoggerMiddleware → HeaderTimeMiddleware → AuthMiddleware → Router
```

### 5.6 لایهٔ شروع و توقف (`bootstrap/locator.py`)

این فایل مسئول:
- ساخت singleton های مورد نیاز (Database, Redis, Auth, SMS, Storage)
- همگام‌سازی enum ها هنگام startup
- بستن اتصال‌ها هنگام shutdown

```python
async def setup():
    # 1. ثبت Config
    loc.registerSingleton("Configs", lambda: cfg)

    # 2. اتصال Redis
    await loc.registerSingletonAsync("AsyncRedisAdapter", ...)

    # 3. اتصال PostgreSQL
    loc.registerSingleton("SQLAlchemyAdapter", ...)

    # 4. همگام‌سازی enum ها
    await loc.get("SQLAlchemyAdapter").enums_sync()

    # 5. سایر سرویس‌ها
    loc.registerSingleton("SMSAdapter", ...)
    loc.registerSingleton("FileStorageService", ...)

async def close():
    await loc.get("SQLAlchemyAdapter").dispose()
```

---

## ۶. مدیریت خطا

### سطح Exception
- هر exception باید معادل یک status code HTTP مشخص باشد.
- پیام خطا باید برای کاربر قابل‌فهم باشد (از `TextApp.get()` استفاده کنید).
- stack trace هرگز به کلاینت فرستاده نشود.

### Errhandler
یک کلاس `Errhandler` با متدهای استاتیک:
- `validation_error(request, exc)` → پاسخ 422 ساختاریافته
- `general_error(request, exc)` → پاسخ خطای عمومی با وضعیت مناسب

### استثناهای رایج پروژه

| Exception | Status | کاربرد |
|---|---|---|
| `Exception400` | 400 | ورودی نامعتبر |
| `Exception400AlreadyExist` | 400 | رکورد تکراری |
| `Exception401MissingToken` | 401 | هدر Authorization وجود ندارد |
| `Exception401ExpiredToken` | 401 | توکن منقضی شده |
| `Exception404` | 404 | منبع یافت نشد |
| `Exception400OTPExpired` | 400 | OTP منقضی شده |
| `Exception404OTPNotRequested` | 404 | OTP درخواست نشده |
| `Exception503SMS` | 503 | سرویس SMS از دسترس خارج |

---

## ۷. تست و کیفیت کد

### ابزارها

| ابزار | وظیفه | پیکربندی |
|---|---|---|
| `ruff` | lint + format | `pyproject.toml` |
| `mypy` | type checking | `mypy.ini` |
| `pyright` | type checking (VS Code) | `pyrightconfig.json` |
| `flake8` | PEP 8 style | `.flake8` |
| `pylint` | کدQuality | `.pylintrc` |
| `isort` | مرتب‌سازی imports | `.isort.cfg` |

### قوانین کیفیت
- هیچ lint error نباید commit شود.
- type hints برای تمام public API ها الزامی است.
- هیچ خطی نباید بیش از ۱۲۰ کاراکتر باشد.

---

## ۸. استقرار (Deploy)

### Docker Compose
حداقل‌ترین compose شامل:
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: db_app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data

  redis:
    image: redis:7
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
```

### اجرای توسعه
```bash
# از طریق Python module
python -m app.main

# یا مستقیم
uvicorn bootstrap.api:app --host 0.0.0.0 --port 8001 --reload
```

### اجرای تولید
```bash
WORKERS=$(( $(nproc) * 2 + 1 ))
gunicorn bootstrap.api:app \
  -w $WORKERS \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080
```

### Alembic migrations
```bash
# ایجاد migration جدید
alembic revision --autogenerate -m "description"

# اعمال migrations
alembic upgrade head

# بررسی وضعیت
alembic history --verbose
```

---

## چک‌لیست شروع پروژهٔ جدید

- [ ] پوشه‌بندی مطابق قالب این سند
- [ ] `configs.py` با pydantic-settings ساخته شده
- [ ] `TableMixin` و `EnumMixin` تعریف شده
- [ ] `locator_service.py` پیاده‌سازی شده
- [ ] `exceptions.py` شامل exception های مورد نیاز
- [ ] `bootstrap/locator.py` سرویس‌ها را ثبت می‌کند
- [ ] middleware ها در `bootstrap/api.py` ثبت شده‌اند
- [ ] هر router در فایل جداگانه
- [ ] `.env.example` برای مستندات موجود است
- [ ] `docker-compose.yml` سرویس‌های پایه را شامل می‌شود
- [ ] قواعد lint در `pyproject.toml` تنظیم شده‌اند
