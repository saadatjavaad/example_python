from typing import Dict
from backbone.db.sqlalchemy_db_based import EnumMixin

"""
اینام ها رکورد ها مشترک بین همه ارگان ها میباشد 

اینام ها همیشه نقش پدر در ارتباط ات رو داره 

اگر فرزند بتواند چند اینام را انتخاب کند ارتباط چند به چند است 
"""


class ThemeTypeEnum(EnumMixin):
    __tablename__ = "theme_type_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "DARK": "dark",
            "LIGHT": "light",
            "SYSTEM": "system",
        }


class LanguageTypeEnum(EnumMixin):
    __tablename__ = "language_type_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "FA": "fa",
            "EN": "en",
            "AR": "ar",
        }


class UserMetricTypeEnum(EnumMixin):
    __tablename__ = "user_metric_type_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "WEIGHT": "health:weight_kg",
            "HEIGHT": "health:height_cm",
            "ENVIRONMENT_SATISFACTION": "hr:1-10",  # رضایت از محیط کار (۱ تا ۱۰)
            "WORK_INTEREST": "hr:1-10",  # علاقه به پروژه/کار فعلی
            "BURNOUT_LEVEL": "hr:1-10",  # میزان فرسودگی شغلی
            "MOTIVATION_SCORE": "hr:1-10",  # انگیزه فردی
            "TEAM_COLLABORATION": "hr:1-10",  # تعامل با تیم
        }


class PermissionEnum(
    EnumMixin
):  # TODO بعدا یک سرویس بیاریم بالا هر بار نیاز نباشه برای بررسی به دیتابیس بریم و از کش استفاده کنیم
    __tablename__ = "permissions_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "SYS_REBOOT": "system:reboot",
            "SYS_VIEW_LOGS": "system:view_logs",
            "SYS_MANAGE_BACKUPS": "system:manage_backups",
            "USERS_CREATE": "users:create",
            "USERS_READ": "users:view",
            "USERS_UPDATE": "users:edit",
            "USERS_DELETE": "users:delete",
            "USERS_MANAGE_ROLES": "users:manage_roles",  # تغییر نقش کاربران
            "BILLING_VIEW_REPORTS": "billing:view_reports",
            "BILLING_ISSUE_REFUND": "billing:issue_refund",  # بازگشت وجه
            "BILLING_MANAGE_GATEWAYS": "billing:manage_gateways",
            "PRODUCT_CREATE": "products:create",
            "PRODUCT_UPDATE": "products:edit",
            "PRODUCT_DELETE": "products:delete",
            "CONTENT_PUBLISH": "content:publish",
            "TICKETS_READ": "tickets:view",
            "TICKETS_REPLY": "tickets:reply",
            "TICKETS_CLOSE": "tickets:close",
            "TICKETS_ASSIGN": "tickets:assign",  # ارجاع تیکت به دیگران
            "API_GENERATE_KEYS": "api:generate_keys",
            "API_VIEW_WEBHOOKS": "api:view_webhooks",
        }


class SlotAccessTypeEnum(EnumMixin):
    """نوع سانس از نظر سطح دسترسی، حضور تماشاگر و مدل بهره‌برداری"""

    __tablename__ = "slot_type_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "PUBLIC": "public",  # عمومی: خرید بلیط برای تمام عموم آزاد است
            "PRIVATE": "private",  # اختصاصی/دربست: رزرو کامل توسط یک شخص یا گروه خاص
            "ORGANIZATIONAL": "organizational",  # سازمانی: قرارداد با ارگان‌ها، شرکت‌ها یا مدارس
            "EVENT": "event",  # رویدادی/مسابقه‌ای: استفاده‌کنندگان محدود، سکو برای تماشاگران آزاد
        }


class ScheduleRecurrenceEnum(EnumMixin):
    """الگوی تکرار برنامه زمانی سانس: یک‌باره، هفتگی، روز مشخص ماه، الگوی موقعیتی ماه و کران"""

    __tablename__ = "schedule_recurrence_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            "ONETIME": "onetime",  # تک جلسه
            "WEEKLY": "weekly",  # هفتگی (مثلاً هر چهارشنبه)
            "MONTHLY": "monthly",  # روز مشخص از ماه (مثلاً ۲۵ام هر ماه)
            "MONTHLY_RELATIVE": "monthly_relative",  # الگوی موقعیتی در ماه (مثلاً چهارشنبه آخر ماه)
        }


class SlotRoleEnum(EnumMixin):
    """
    مسئولیت‌های جامع افراد در انواع سانس‌ها، رویدادها، همایش‌ها و برنامه‌های زمان‌بندی‌شده.
    """

    __tablename__ = "slot_role_enum"

    @classmethod
    def get_enum_map(cls) -> Dict[str, str]:
        return {
            # --- نقش‌های مدیریتی و برگزاری (Management & Ownership) ---
            "MEMBER": "general:member",  # عضو / شرکت‌کننده
            "HOST": "event:host",  # میزبان
            "PRODUCER": "event:producer",  # تهیه کننده / برگزارکننده
            "ORGANIZER": "event:organizer",  # مدیر اجرایی / سازمان‌دهنده
            "MANAGER": "event:manager",  # مدیر سانس / مدیر سالن
            "SUPERVISOR": "event:supervisor",  # ناظر / سوپروایزر
            # --- نقش‌های تخصصی، آموزشی و محتوایی (Content & Instruction) ---
            "SPEAKER": "content:speaker",  # سخنران / ارائه دهنده
            "INSTRUCTOR": "content:instructor",  # مدرس / استاد
            "COACH": "sports:coach",  # مربی ورزشی
            "MODERATOR": "content:moderator",  # گرداننده پنل / مجری
            "JUDGE": "sports:judge",  # داور / ارزیاب
            # --- نقش‌های فنی، ایمنی و پشتیبانی (Technical & Safety) ---
            "TECHNICAL_SUPPORT": "tech:support",  # مسئول فنی / پشتیبان تجهیزات
            "LIFEGUARD": "sports:lifeguard",  # غریق‌نجات
            "FIRST_AIDER": "safety:first_aider",  # امدادگر / پزشک سالن
            "SECURITY": "safety:security",  # حراست / انتظامات
            # --- نقش‌های تشریفات و خدمات (Hospitality & Staff) ---
            "RECEPTIONIST": "service:receptionist",  # پذیرش‌گر / ثبت‌نام
            "USHER": "service:usher",  # راهنمای سالن / تشریفات
            "OPERATOR": "service:operator",  # اپراتور سیستم / گیت
            # --- سایر ---
            "ASSISTANT": "general:assistant",  # دستیار / کمک‌کار
        }
