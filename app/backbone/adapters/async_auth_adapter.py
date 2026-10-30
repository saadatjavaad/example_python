import asyncio
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AsyncRedisAuthAdapter:
    def __init__(
        self,
        redis_client: Redis,
        jwt_secret_key: str | None = None,
        jwt_algorithm: str = "HS256",
        access_token_expire_day: int = 1,
        refresh_token_expire_days: int = 15,
        otp_expire_seconds: int = 120,
    ):
        """
        تزریق شیء Redis و تنظیمات مربوط به توکن‌ها.
        ارتباط و مدیریت چرخه حیات اتصال Redis کلاً خارج از این کلاس انجام می‌شود.
        """
        self.redis_client = redis_client

        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
        self.access_token_ttl = timedelta(days=access_token_expire_day)
        self.refresh_token_ttl = timedelta(days=refresh_token_expire_days)
        self.otp_ttl = otp_expire_seconds

    def _extract_raw_token(self, token: str) -> str:
        """جداکردن پیشوند Bearer از توکن ورودی در صورت وجود"""
        if token and token.startswith("Bearer "):
            return token[7:].strip()
        return token.strip() if token else token

    # ------------------------------------------------------------------
    # بخش ۱: مدیریت OTP
    # ------------------------------------------------------------------

    async def generate_otp(self, user_id: str, length: int = 6) -> tuple[str, datetime]:
        """تولید رمز یک‌بارمصرف (OTP) و ذخیره آن در ردیس با زمان انقضا"""
        digits = "0123456789"
        otp_code = "".join(secrets.choice(digits) for _ in range(length))

        key = f"otp:{user_id}"
        await self.redis_client.set(key, otp_code, ex=self.otp_ttl)
        expires_at = datetime.now() + timedelta(seconds=self.otp_ttl)

        return otp_code, expires_at

    async def verify_otp_and_generate_tokens(
        self, user_id: str, input_otp: str, device_metadata: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """بررسی اعتبار OTP و در صورت صحت، پاک‌سازی آن و تولید توکن‌ها به همراه ذخیره متادیتا"""
        otp_key = f"otp:{user_id}"
        stored_otp = await self.redis_client.get(otp_key)
        if stored_otp is None:
            return None

        if isinstance(stored_otp, bytes):
            stored_otp = stored_otp.decode("utf-8")

        if stored_otp != input_otp:
            return None

        # حذف OTP پس از استفاده موفق
        await self.redis_client.delete(otp_key)

        # تولید توکن‌های جدید
        tokens = await self.create_tokens(
            user_id=user_id, device_metadata=device_metadata
        )
        return tokens

    async def create_tokens(
        self, user_id: str, device_metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """تولید Access Token و Refresh Token همراه با پیشوند Bearer و ذخیره‌سازی داده‌های جلسه در ردیس"""
        now = datetime.now(timezone.utc)

        # شناسه منحصربه‌فرد برای این Session/JTI
        session_id = secrets.token_hex(16)
        user_id = str(user_id)

        # ساختار Payload توکن‌ها
        access_payload = {
            "sub": user_id,
            "type": "access",
            "sid": session_id,
            "iat": now,
            "exp": now + self.access_token_ttl,
        }

        refresh_payload = {
            "sub": user_id,
            "type": "refresh",
            "sid": session_id,
            "iat": now,
            "exp": now + self.refresh_token_ttl,
        }

        raw_access_token = jwt.encode(
            access_payload, self.jwt_secret_key, algorithm=self.jwt_algorithm
        )
        raw_refresh_token = jwt.encode(
            refresh_payload, self.jwt_secret_key, algorithm=self.jwt_algorithm
        )

        # افزودن پیشوند Bearer
        access_token = f"Bearer {raw_access_token}"
        refresh_token = f"Bearer {raw_refresh_token}"

        # ساخت ساختار داده برای ذخیره‌سازی در ردیس
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": now.isoformat(),
            "device_metadata": device_metadata,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        # کلید اصلی برای دسترسی بر اساس session_id
        session_key = f"session:{session_id}"
        # نگاشت برای دسترسی آسان و سریع از طریق user_id به تمام نشست‌های فعال کاربر
        user_sessions_key = f"user_sessions:{user_id}"

        ttl_seconds = int(self.refresh_token_ttl.total_seconds())

        # ذخیره داده‌های جلسه
        await self.redis_client.set(
            session_key, json.dumps(session_data), ex=ttl_seconds
        )
        # افزودن شناسه جلسه به مجموعه جلسات کاربر
        await self.redis_client.sadd(user_sessions_key, session_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def verify_token(
        self, token: str, expected_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """بررسی صحت امضا، انقضای توکن، نوع توکن و فعال بودن نشست مربوطه در ردیس"""
        raw_token = self._extract_raw_token(token)
        try:
            payload = jwt.decode(
                raw_token, self.jwt_secret_key, algorithms=[self.jwt_algorithm]
            )

        except jwt.ExpiredSignatureError as e:
            logger.warning("TOKEN EXPIRED: %s", e)
            return None

        except jwt.InvalidTokenError as e:
            logger.warning("INVALID TOKEN: %s (%s)", e, type(e).__name__)
            return None

        # بررسی نوع توکن (access یا refresh)
        if payload.get("type") != expected_type:
            return None

        session_id = payload.get("sid")
        if not session_id:
            return None

        # بررسی وجود داشتن جلسه فعال در ردیس
        session_key = f"session:{session_id}"
        session_raw = await self.redis_client.get(session_key)

        if not session_raw:
            return None

        return payload

    async def get_info_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """استخراج کامل اطلاعات و متادیتای ذخیره‌شده بر اساس توکن ورودی"""
        payload = await self.verify_token(token)
        if not payload:
            return None

        session_id = payload.get("sid")
        session_key = f"session:{session_id}"
        session_raw = await self.redis_client.get(session_key)

        if not session_raw:
            return None

        return json.loads(session_raw)

    async def get_info_by_user_id(self, user_id: str) -> Dict[str, Any]:
        """دریافت تمام جلسات فعال و متادیتای مربوط به یک کاربر بر اساس user_id"""
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis_client.smembers(user_sessions_key)

        active_sessions = []
        expired_session_ids = []

        for sid in session_ids:
            session_key = f"session:{sid}"
            session_raw = await self.redis_client.get(session_key)

            if session_raw:
                active_sessions.append(json.loads(session_raw))
            else:
                expired_session_ids.append(sid)

        # پاک‌سازی شناسه‌های منقضی‌شده از Set مربوط به کاربر
        if expired_session_ids:
            await self.redis_client.srem(user_sessions_key, *expired_session_ids)

        return {
            "user_id": user_id,
            "active_sessions_count": len(active_sessions),
            "sessions": active_sessions,
        }

    async def revoke_session(self, token: str) -> bool:
        """ابطال یک جلسه خاص (Logout) بر اساس توکن"""
        raw_token = self._extract_raw_token(token)
        try:
            payload = jwt.decode(
                raw_token,
                self.jwt_secret_key,
                algorithms=[self.jwt_algorithm],
                options={"verify_exp": False},
            )
            session_id = payload.get("sid")
            user_id = payload.get("sub")

            if session_id and user_id:
                await self.redis_client.delete(f"session:{session_id}")
                await self.redis_client.srem(f"user_sessions:{user_id}", session_id)
                return True
        except jwt.InvalidTokenError:
            pass
        return False

    async def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, str]]:
        """
        اعتبارسنجی Refresh Token و صدور توکن‌های جدید (Access Token و Refresh Token جدید)
        """
        raw_token = self._extract_raw_token(refresh_token)

        # ۱. بررسی صحت امضا و انقضای JWT
        try:
            payload = jwt.decode(
                raw_token, self.jwt_secret_key, algorithms=[self.jwt_algorithm]
            )
        except jwt.ExpiredSignatureError as e:
            logger.warning("TOKEN EXPIRED: %s", e)
            return None

        except jwt.InvalidTokenError as e:
            logger.warning("INVALID TOKEN: %s (%s)", e, type(e).__name__)
            return None

        # ۲. اطمینان از اینکه توکن ارسالی واقعاً از نوع Refresh Token است
        if payload.get("type") != "refresh":
            return None

        session_id = payload.get("sid")
        user_id = payload.get("sub")
        if not session_id or not user_id:
            return None

        # ۳. بررسی فعال بودن Session در ردیس
        session_key = f"session:{session_id}"
        session_raw = await self.redis_client.get(session_key)
        if not session_raw:
            return None

        session_data = json.loads(session_raw)
        device_metadata = session_data.get("device_metadata", {})

        # ۴. ابطال جلسه قبلی جهت امنیت (Token Rotation)
        await self.redis_client.delete(session_key)
        await self.redis_client.srem(f"user_sessions:{user_id}", session_id)
        # ۵. تولید توکن‌های جدید
        new_tokens = await self.create_tokens(
            user_id=user_id, device_metadata=device_metadata
        )
        return new_tokens


async def test_auth_flow(auth_adapter: AsyncRedisAuthAdapter):

    user_id = "12345"

    # 1. ساخت توکن اولیه
    print("\n=== CREATE TOKENS ===")

    tokens = await auth_adapter.create_tokens(
        user_id=user_id, device_metadata={"device": "Windows", "ip": "127.0.0.1"}
    )

    old_access = tokens["access_token"]
    old_refresh = tokens["refresh_token"]

    print("ACCESS:")
    print(old_access)

    print("\nREFRESH:")
    print(old_refresh)

    # 2. بررسی refresh token اولیه
    print("\n=== VERIFY OLD REFRESH ===")

    payload = await auth_adapter.verify_token(old_refresh, expected_type="refresh")

    print(payload)

    # 3. اجرای Refresh
    print("\n=== REFRESH TOKEN ===")

    new_tokens = await auth_adapter.refresh_access_token(old_refresh)

    print(new_tokens)

    if new_tokens is None:
        print("REFRESH FAILED")
        return

    new_access = new_tokens["access_token"]
    new_refresh = new_tokens["refresh_token"]

    # 4. تست اینکه refresh قبلی دیگر معتبر نیست
    print("\n=== VERIFY OLD REFRESH AFTER ROTATION ===")

    old_refresh_check = await auth_adapter.verify_token(
        old_refresh, expected_type="refresh"
    )

    print(old_refresh_check)

    # 5. تست refresh جدید
    print("\n=== VERIFY NEW REFRESH ===")

    new_refresh_check = await auth_adapter.verify_token(
        new_refresh, expected_type="refresh"
    )

    print(new_refresh_check)

    # 6. تست access جدید
    print("\n=== VERIFY NEW ACCESS ===")

    new_access_check = await auth_adapter.verify_token(
        new_access, expected_type="access"
    )

    print(new_access_check)


async def main():
    redis_client = Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )

    auth_adapter = AsyncRedisAuthAdapter(
        redis_client=redis_client,
        jwt_secret_key="SECRET_KEY_FROM_ENV",
        access_token_expire_day=15,
        refresh_token_expire_days=7,
        otp_expire_seconds=120,
    )

    try:
        await test_auth_flow(auth_adapter)

    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
