# This file is auto-generated. Do not modify manually.

from enum import Enum


class LanguageTypeEnum(str, Enum):
    FA = "fa"  # FA
    EN = "en"  # EN
    AR = "ar"  # AR


class PermissionsEnum(str, Enum):
    SYS_REBOOT = "system:reboot"  # SYS_REBOOT
    SYS_VIEW_LOGS = "system:view_logs"  # SYS_VIEW_LOGS
    SYS_MANAGE_BACKUPS = "system:manage_backups"  # SYS_MANAGE_BACKUPS
    USERS_CREATE = "users:create"  # USERS_CREATE
    USERS_READ = "users:view"  # USERS_READ
    USERS_UPDATE = "users:edit"  # USERS_UPDATE
    USERS_DELETE = "users:delete"  # USERS_DELETE
    USERS_MANAGE_ROLES = "users:manage_roles"  # USERS_MANAGE_ROLES
    BILLING_VIEW_REPORTS = "billing:view_reports"  # BILLING_VIEW_REPORTS
    BILLING_ISSUE_REFUND = "billing:issue_refund"  # BILLING_ISSUE_REFUND
    BILLING_MANAGE_GATEWAYS = "billing:manage_gateways"  # BILLING_MANAGE_GATEWAYS
    PRODUCT_CREATE = "products:create"  # PRODUCT_CREATE
    PRODUCT_UPDATE = "products:edit"  # PRODUCT_UPDATE
    PRODUCT_DELETE = "products:delete"  # PRODUCT_DELETE
    CONTENT_PUBLISH = "content:publish"  # CONTENT_PUBLISH
    TICKETS_READ = "tickets:view"  # TICKETS_READ
    TICKETS_REPLY = "tickets:reply"  # TICKETS_REPLY
    TICKETS_CLOSE = "tickets:close"  # TICKETS_CLOSE
    TICKETS_ASSIGN = "tickets:assign"  # TICKETS_ASSIGN
    API_GENERATE_KEYS = "api:generate_keys"  # API_GENERATE_KEYS
    API_VIEW_WEBHOOKS = "api:view_webhooks"  # API_VIEW_WEBHOOKS


class ScheduleRecurrenceEnum(str, Enum):
    ONETIME = "onetime"  # ONETIME
    WEEKLY = "weekly"  # WEEKLY
    MONTHLY = "monthly"  # MONTHLY
    MONTHLY_RELATIVE = "monthly_relative"  # MONTHLY_RELATIVE


class SlotRoleEnum(str, Enum):
    MEMBER = "general:member"  # MEMBER
    HOST = "event:host"  # HOST
    PRODUCER = "event:producer"  # PRODUCER
    ORGANIZER = "event:organizer"  # ORGANIZER
    MANAGER = "event:manager"  # MANAGER
    SUPERVISOR = "event:supervisor"  # SUPERVISOR
    SPEAKER = "content:speaker"  # SPEAKER
    INSTRUCTOR = "content:instructor"  # INSTRUCTOR
    COACH = "sports:coach"  # COACH
    MODERATOR = "content:moderator"  # MODERATOR
    JUDGE = "sports:judge"  # JUDGE
    TECHNICAL_SUPPORT = "tech:support"  # TECHNICAL_SUPPORT
    LIFEGUARD = "sports:lifeguard"  # LIFEGUARD
    FIRST_AIDER = "safety:first_aider"  # FIRST_AIDER
    SECURITY = "safety:security"  # SECURITY
    RECEPTIONIST = "service:receptionist"  # RECEPTIONIST
    USHER = "service:usher"  # USHER
    OPERATOR = "service:operator"  # OPERATOR
    ASSISTANT = "general:assistant"  # ASSISTANT


class SlotTypeEnum(str, Enum):
    PUBLIC = "public"  # PUBLIC
    PRIVATE = "private"  # PRIVATE
    ORGANIZATIONAL = "organizational"  # ORGANIZATIONAL
    EVENT = "event"  # EVENT


class ThemeTypeEnum(str, Enum):
    DARK = "dark"  # DARK
    LIGHT = "light"  # LIGHT
    SYSTEM = "system"  # SYSTEM


class UserMetricTypeEnum(str, Enum):
    WEIGHT = "health:weight_kg"  # WEIGHT
    HEIGHT = "health:height_cm"  # HEIGHT
    ENVIRONMENT_SATISFACTION = "hr:1-10"  # ENVIRONMENT_SATISFACTION
    WORK_INTEREST = "hr:1-10"  # WORK_INTEREST
    BURNOUT_LEVEL = "hr:1-10"  # BURNOUT_LEVEL
    MOTIVATION_SCORE = "hr:1-10"  # MOTIVATION_SCORE
    TEAM_COLLABORATION = "hr:1-10"  # TEAM_COLLABORATION

