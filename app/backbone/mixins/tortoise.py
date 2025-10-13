from datetime import datetime, timedelta
from pydantic import ValidationError
from tortoise import fields, models  # type: ignore


class TortoiseMixinTimestamp(models.Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class TortoiseMixinSoftDelete(models.Model):
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True


class TortoiseMixinID(models.Model):
    id = fields.IntField(pk=True)

    class Meta:
        abstract = True


class TortoiseMixinPass(models.Model):
    password = fields.CharField(max_length=128, null=True)

    class Meta:
        abstract = True


class TortoiseMixinUserUsername(models.Model):
    username = fields.CharField(max_length=50, unique=True)

    class Meta:
        abstract = True


class TortoiseMixinUserId(models.Model):
    user_id = fields.IntField(unique=True)

    class Meta:
        abstract = True


class TortoiseMixinContactOptional(models.Model):
    """ایمیل و شماره تلفن اختیاری هستند"""

    phone = fields.CharField(max_length=14, unique=True, null=True)
    email = fields.CharField(max_length=100, unique=True, null=True)

    class Meta:
        abstract = True


class TortoiseMixinContactRequired(models.Model):
    """ایمیل و شماره تلفن اجباری هستند"""

    phone = fields.CharField(max_length=14, unique=True)
    email = fields.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True


class TortoiseMixinContactAtLeastOne(models.Model):
    phone = fields.CharField(max_length=14, unique=True, null=True)
    email = fields.CharField(max_length=100, unique=True, null=True)

    class Meta:
        abstract = True

    async def validate(self):
        """حداقل یکی از فیلدها پر باشد"""
        if not self.phone and not self.email:
            raise ValidationError(
                "حداقل یکی از فیلدهای phone یا email باید مقدار داشته باشد."
            )

    async def save(self, *args, **kwargs):
        await self.validate()  # ولیدیشن قبل از ذخیره
        await super().save(*args, **kwargs)


class TortoiseMixinToken(models.Model):
    token = fields.CharField(max_length=255, null=True)
    refresh_token = fields.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class TortoiseMixinOtp(models.Model):
    otp = fields.IntField(null=True)
    otp_exp = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

    async def set_otp(self, otp_code: int, expire_minutes: int = 5):
        self.otp = otp_code
        self.otp_exp = datetime.utcnow() + timedelta(minutes=expire_minutes)
        await self.save(update_fields=["otp", "otp_exp"])

    def is_otp_valid(self, otp_code: int) -> bool:
        if not self.otp or not self.otp_exp:
            return False
        if self.otp != otp_code:
            return False
        return datetime.utcnow() <= self.otp_exp


class TortoiseMixinUserStatus(models.Model):
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)

    class Meta:
        abstract = True


class TortoiseMixinBase(
    TortoiseMixinID,
    TortoiseMixinTimestamp,
    TortoiseMixinSoftDelete,
):
    class Meta:
        abstract = True
