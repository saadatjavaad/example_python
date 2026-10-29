import uuid
from datetime import date as dt
from datetime import datetime, time
from typing import List, Optional

from backbone.db.db_enums import (
    LanguageTypeEnum,
    PermissionEnum,
    ScheduleRecurrenceEnum,
    SlotAccessTypeEnum,
    SlotRoleEnum,
    ThemeTypeEnum,
    UserMetricTypeEnum,
)
from backbone.db.sqlalchemy_db_based import (
    TableMixin,
)
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class User(TableMixin):
    __tablename__ = "users"
    name: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    given_name: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(120),
        unique=True,
        nullable=True,
    )

    phone: Mapped[str] = mapped_column(
        String(13),
        unique=True,
        index=True,
        nullable=False,
    )

    birthday: Mapped[Optional[dt]] = mapped_column(
        Date,
        nullable=True,
    )

    is_profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    profile_image: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    permissions: Mapped[List["PermissionEnum"]] = relationship(
        "PermissionEnum",
        secondary="user_permissions",
        primaryjoin=lambda: User.id == UserPermissions.user_id,
        secondaryjoin=lambda: PermissionEnum.id == UserPermissions.permission_enum_id,
        viewonly=True,
    )

    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings",
        foreign_keys="UserSettings.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    slots: Mapped[List["SlotMemberships"]] = relationship(
        "SlotMemberships",
        foreign_keys="SlotMemberships.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    attendance: Mapped[List["SlotAttendance"]] = relationship(
        "SlotAttendance",
        foreign_keys="SlotAttendance.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    work: Mapped[List["Work"]] = relationship(
        "Work",
        foreign_keys="Work.user_id",
        back_populates="user",
    )
    gifts: Mapped[List["UserGift"]] = relationship(
        "UserGift",
        foreign_keys="UserGift.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sent_feedbacks: Mapped[List["UserFeedback"]] = relationship(
        "UserFeedback",
        foreign_keys="UserFeedback.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )

    received_feedbacks: Mapped[List["UserFeedback"]] = relationship(
        "UserFeedback",
        foreign_keys="UserFeedback.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )
    sent_notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        foreign_keys="Notification.sender_id",
        back_populates="sender",
    )

    notification_recipients: Mapped[List["NotificationRecipient"]] = relationship(
        "NotificationRecipient",
        foreign_keys="NotificationRecipient.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )

    progress_logs: Mapped[List["UserProgressLog"]] = relationship(
        "UserProgressLog",
        foreign_keys="UserProgressLog.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserPermissions(TableMixin):
    __tablename__ = "user_permissions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    permission_enum_id: Mapped[int] = mapped_column(
        ForeignKey("permissions_enum.id", ondelete="CASCADE"), primary_key=True
    )


class UserSettings(TableMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="settings",
    )

    theme_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("theme_type_enum.id", ondelete="SET NULL"),
        nullable=True,
    )
    theme: Mapped[Optional["ThemeTypeEnum"]] = relationship()

    language_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("language_type_enum.id", ondelete="SET NULL"),
        nullable=True,
    )
    language: Mapped[Optional["LanguageTypeEnum"]] = relationship()

    enable_notifications: Mapped[bool] = mapped_column(default=True)
    extra_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class UserProgressLog(TableMixin):
    __tablename__ = "user_progress_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="progress_logs"
    )

    metric_type_enum_id: Mapped[int] = mapped_column(
        ForeignKey("user_metric_type_enum.id", ondelete="RESTRICT"),
        index=True,
    )
    metric_type_enum: Mapped["UserMetricTypeEnum"] = relationship()

    value: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Slot(TableMixin):

    __tablename__ = "slots"

    schedules: Mapped[List["SlotSchedule"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )

    title: Mapped[str] = mapped_column(String(100))

    capacity: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # ظرفیت سانس

    # کلیدهای خارجی به اینام‌ها
    slot_type_id: Mapped[int] = mapped_column(
        ForeignKey("slot_type_enum.id", ondelete="RESTRICT")
    )
    slot_type: Mapped["SlotAccessTypeEnum"] = relationship()

    memberships: Mapped[List["SlotMemberships"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )

    gates: Mapped[List["Gate"]] = relationship(secondary="slot_gate")

    attendance: Mapped[List["SlotAttendance"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )


class SlotSchedule(TableMixin):
    __tablename__ = "slot_schedules"

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"), index=True
    )
    slot: Mapped["Slot"] = relationship(back_populates="schedules")

    schedules_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("schedule_recurrence_enum.id", ondelete="RESTRICT"), nullable=True
    )
    schedules_type: Mapped[Optional["ScheduleRecurrenceEnum"]] = relationship()

    date: Mapped[Optional[dt]] = mapped_column(
        nullable=True
    )  # برای سانس های تک جلسه یا تاریخ خاص

    day_number: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # شماره روز در حالت هفتگی و ماهانه (مثلاً 1 تا 31 برای روزهای ماه) یا در حالت هفتگی 0-6 و در حالت ریلاتیو  همان شماره روز هفته است

    monthly_relative_week: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # هفته در حالت ماهانه نسبی (مثلاً 1 تا 5 برای هفته‌های ماه) و -۱ یعنی آخرین هفته ماه

    start_time: Mapped[time] = mapped_column(nullable=False)  # مثلاً 08:00
    end_time: Mapped[time] = mapped_column(nullable=False)  # مثلاً 10:00
    # بازه اعتبار در صورت حالت های پیوسته مثل  هفتگی
    valid_from_date: Mapped[Optional[dt]] = mapped_column(
        Date, nullable=True
    )  # تاریخ شروع اعتبار بازه
    valid_until_date: Mapped[Optional[dt]] = mapped_column(
        Date, nullable=True
    )  # تاریخ پایان اعتبار بازه


class SlotMemberships(TableMixin):
    __tablename__ = "slot_memberships"

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"), primary_key=True
    )
    slot: Mapped["Slot"] = relationship(back_populates="memberships")

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="slots",
    )
    role_enum_id: Mapped[int] = mapped_column(
        ForeignKey("slot_role_enum.id", ondelete="RESTRICT"), primary_key=True
    )
    role_enum: Mapped["SlotRoleEnum"] = relationship()


class Gate(TableMixin):
    __tablename__ = "gates"

    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4()),
    )
    is_active: Mapped[bool] = mapped_column(default=True)


class SlotGate(TableMixin):
    __tablename__ = "slot_gate"

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"), primary_key=True
    )
    gate_id: Mapped[int] = mapped_column(
        ForeignKey("gates.id", ondelete="CASCADE"), primary_key=True
    )


class SlotAttendance(TableMixin):
    __tablename__ = "slot_attendances"

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"), index=True
    )
    slot: Mapped["Slot"] = relationship(
        "Slot",
        foreign_keys=[slot_id],
        back_populates="attendance",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="attendance",
    )
    gate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("gates.id", ondelete="SET NULL"), nullable=True
    )
    gate: Mapped[Optional["Gate"]] = relationship(
        "Gate",
        foreign_keys=[gate_id],
    )
    attendance_date: Mapped[dt] = mapped_column(nullable=False, index=True)
    check_in_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    check_out_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Work(TableMixin):

    __tablename__ = "works"

    schedules: Mapped[List["WorkSchedule"]] = relationship(
        back_populates="work", cascade="all, delete-orphan"
    )

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="work",
    )


class WorkSchedule(TableMixin):
    __tablename__ = "work_schedules"

    work_id: Mapped[int] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), index=True
    )
    work: Mapped["Work"] = relationship(back_populates="schedules")

    schedules_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("schedule_recurrence_enum.id", ondelete="RESTRICT"), nullable=True
    )
    schedules_type: Mapped[Optional["ScheduleRecurrenceEnum"]] = relationship()

    date: Mapped[Optional[dt]] = mapped_column(
        nullable=True
    )  # برای کار های تک جلسه یا تاریخ خاص

    day_number: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # شماره روز در حالت هفتگی و ماهانه (مثلاً 1 تا 31 برای روزهای ماه) یا در حالت هفتگی 0-6 و در حالت ریلاتیو  همان شماره روز هفته است

    monthly_relative_week: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # هفته در حالت ماهانه نسبی (مثلاً 1 تا 5 برای هفته‌های ماه) و -۱ یعنی آخرین هفته ماه

    start_time: Mapped[time] = mapped_column(nullable=False)  # مثلاً 08:00
    end_time: Mapped[time] = mapped_column(nullable=False)  # مثلاً 10:00
    # بازه اعتبار در صورت حالت های پیوسته مثل  هفتگی
    valid_from_date: Mapped[Optional[dt]] = mapped_column(
        Date, nullable=True
    )  # تاریخ شروع اعتبار بازه
    valid_until_date: Mapped[Optional[dt]] = mapped_column(
        Date, nullable=True
    )  # تاریخ پایان اعتبار بازه


class Gift(TableMixin):
    """جدول تعریف گیفت‌ها و جوایز سیستم"""

    __tablename__ = "gifts"

    title: Mapped[str] = mapped_column(String(100), nullable=False)  # عنوان گیفت
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # توضیحات

    value: Mapped[Optional[float]] = mapped_column(nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ارتباط با کاربران دریافت‌کننده
    user_gifts: Mapped[List["UserGift"]] = relationship(
        back_populates="gift", cascade="all, delete-orphan"
    )


class UserGift(TableMixin):
    """جدول گیفت‌های تعلق گرفته به کاربران (تاریخچه و وضعیت استفاده)"""

    __tablename__ = "user_gifts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="gifts",
    )
    gift_id: Mapped[int] = mapped_column(
        ForeignKey("gifts.id", ondelete="CASCADE"), index=True
    )
    gift: Mapped["Gift"] = relationship(back_populates="user_gifts")

    is_gifted: Mapped[bool] = mapped_column(Boolean, default=False)
    gifted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class UserFeedback(TableMixin):
    """
    جدول ثبت بازخوردها، تقدیرها و نکات بین کاربران.
    در صورت تنظیم is_anonymous=True، هویت فرستنده در فرانت‌اند مخفی می‌شود
    اما sender_id و created_by_id همواره جهت پیگیری سیستم ثبت می‌گردد.
    """

    __tablename__ = "user_feedbacks"

    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipient: Mapped["User"] = relationship(
        foreign_keys=[recipient_id], back_populates="received_feedbacks"
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    sender: Mapped["User"] = relationship(
        foreign_keys=[sender_id], back_populates="sent_feedbacks"
    )

    is_anonymous: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default=false()
    )

    title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)


class Notification(TableMixin):

    __tablename__ = "notifications"

    # فرستنده پیام (در صورت سیستمی بودن می‌تواند null باشد)
    sender_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_notifications",
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    recipients: Mapped[List["NotificationRecipient"]] = relationship(
        back_populates="notification", cascade="all, delete-orphan"
    )


class NotificationRecipient(TableMixin):

    __tablename__ = "notification_recipients"

    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    notification: Mapped["Notification"] = relationship(back_populates="recipients")

    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipient: Mapped["User"] = relationship(
        foreign_keys=[recipient_id],
        back_populates="notification_recipients",
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default=false(), index=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
