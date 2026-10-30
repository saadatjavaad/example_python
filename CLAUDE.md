# Gatein Back — Project Context

بک‌اند پروژه Gatein — یک سرویس FastAPI برای مدیریت ورود و خروج کاربران (attendance system) با احراز هویت OTP، مدیریت سانس‌ها، اهدای جوایز، بازخورد کاربران و پیام‌رسانی.

## تکنولوژی‌ها

- **FastAPI** 0.139.2 — وب فریمورک
- **SQLAlchemy 2.0** (Async) — ORM
- **PostgreSQL** 16 — دیتابیس
- **Redis** (async) — کش و نشست
- **PyJWT / python-jose** — توکن‌سازی
- **Kavenegar** — واسط SMS
- **Keycloak** — کلاینت احراز هویت
- **Uvicorn / Gunicorn + UvicornWorker** — سرور

## ساختار پروژه

```
app/
├── main.py                 # نقطه ورود (uvicorn / gunicorn)
├── backbone/               # هسته برنامه
│   ├── configs.py          # Configs (pydantic-settings)
│   ├── exceptions.py       # Exception‌های سفارشی + Errhandler
│   ├── locator_service.py  # DI Container (LocatorService)
│   └── db/
│       ├── sqlalchemy_db_based.py  # TableMixin, SQLAlchemyAdapter, EnumMixin
│       ├── tables.py                 # مدل‌های SQLAlchemy
│       └── db_enums.py               # Enumهای table-based
├── bootstrap/              # راه‌اندازی
└── routers/                # API endpointها
```

## شیوه کدنویسی

- کامنت‌گذاری به فارسی و انگلیسی پذیرفته است
- نام‌گذاری متغیرها و توابع به انگلیسی
- استفاده از Async/Await در تمام لایه‌ها
- پرهیز از Magic Number — تعریف ثابت در بالا
- خط طولی 100 کاراکتر
- Type hints اجباری

---

## Skill: Requesting Code Review

Before merging any feature or completing a major task, dispatch a code reviewer subagent using this skill.

**When to use:**
- After completing a task in subagent-driven development
- After finishing a major feature
- Before merging to `main`

**How to use:**
1. Get git SHAs:
   ```bash
   BASE_SHA=$(git rev-parse HEAD~1)   # or: git merge-base origin/main HEAD
   HEAD_SHA=$(git rev-parse HEAD)
   ```
2. Dispatch a `general-purpose` subagent with the template at [.agents/skills/requesting-code-review/code-reviewer.md](.agents/skills/requesting-code-review/code-reviewer.md)
   - Fill in `{DESCRIPTION}`, `{PLAN_OR_REQUIREMENTS}`, `{BASE_SHA}`, `{HEAD_SHA}`
3. Act on findings: Critical → fix now, Important → fix before proceeding, Minor → defer

**Never skip review** because "it's simple." Hand the reviewer precisely crafted context — never your session history.
