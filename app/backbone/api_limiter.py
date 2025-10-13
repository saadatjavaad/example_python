import json
from backbone.exceptions import BadRequestException
from fastapi import Request, Response
from fastapi_limiter.depends import RateLimiter

from backbone.configs import configs
from backbone.helpers.fastapi_reaquest import RequestHelper
from backbone.helpers.hash import HashHelpers


PREFIX_KEY = "rate_limit_identifier:"
WHITELIST_IPS = frozenset(["127.0.0.1", "80.191.88.109"])
NO_RATE_LIMIT_TAG = "no_rate_limit"


# ========== Rate Limit Identifiers (به ترتیب حساسیت) ==========
class RateLimitIdentifiers:
    @staticmethod
    def generate_random_identifier(length: int = 8) -> str:
        import uuid

        return uuid.uuid4().hex[:length]

    @staticmethod
    def hash_sensitive_data(v: str, hash_len: int) -> str:
        return HashHelpers.hash(v, hash_len)

    @staticmethod
    async def global_identifier(request: Request) -> str:
        """
        سطح حساسیت: بسیار پایین
        برای محدودیت کلی روی تمام درخواست ها
        """
        return f"{PREFIX_KEY}global:all"

    @staticmethod
    async def endpoint_identifier(request: Request) -> str:
        """
        سطح حساسیت: پایین
        محدودیت بر اساس endpoint
        """
        helper = RequestHelper(request)
        path = helper.get_path()
        method = helper.get_method()
        return f"{PREFIX_KEY}endpoint:{method}:{path}"

    @staticmethod
    async def ip_identifier(request: Request) -> str:
        """
        سطح حساسیت: متوسط
        محدودیت بر اساس IP
        """
        helper = RequestHelper(request)
        ip = helper.get_client_ip()
        path = helper.get_path()

        # نادیده گرفتن IP های Whitelist
        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        return f"{PREFIX_KEY}ip:{ip}:{path}"

    @staticmethod
    async def ip_user_agent_identifier(request: Request) -> str:
        """
        سطح حساسیت: متوسط به بالا
        محدودیت بر اساس IP + User Agent
        """
        helper = RequestHelper(request)
        ip = helper.get_client_ip()
        user_agent = helper.get_user_agent()
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        # Hash کردن User Agent برای کاهش طول
        ua_hash = RateLimitIdentifiers.hash_sensitive_data(user_agent or "unknown", 8)

        return f"{PREFIX_KEY}ip_ua:{ip}:{ua_hash}:{path}"

    @staticmethod
    async def ip_user_agent_device_id_identifier(request: Request) -> str:
        """
        سطح حساسیت: بالا
        محدودیت بر اساس IP + User Agent + Device ID
        """
        helper = RequestHelper(request)
        ip = helper.get_client_ip()
        user_agent = helper.get_user_agent()
        device_id = helper.get_header("x-device-id")
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        ua_hash = RateLimitIdentifiers.hash_sensitive_data(user_agent or "unknown", 8)
        device_hash = (
            RateLimitIdentifiers.hash_sensitive_data(device_id, 8)
            if device_id
            else "no_device"
        )

        return f"{PREFIX_KEY}ip_ua_device:{ip}:{ua_hash}:{device_hash}:{path}"

    @staticmethod
    async def session_identifier(request: Request) -> str:
        """
        سطح حساسیت: بالا
        محدودیت بر اساس Session
        """
        helper = RequestHelper(request)
        session_id = helper.get_cookie("session_id") or helper.get_header(
            "x-session-id"
        )
        path = helper.get_path()

        if not session_id:
            # استفاده از IP به عنوان fallback
            return await RateLimitIdentifiers.ip_identifier(request)

        session_hash = RateLimitIdentifiers.hash_sensitive_data(session_id, 12)
        return f"{PREFIX_KEY}session:{session_hash}:{path}"

    @staticmethod
    async def user_id_identifier(request: Request) -> str:
        """
        سطح حساسیت: بسیار بالا
        محدودیت بر اساس User ID (برای کاربران وارد شده)
        """
        helper = RequestHelper(request)

        if not hasattr(request.state, "user_uuid") or not request.state.user_uuid:
            # اگر کاربر وارد نشده، استفاده از IP
            return await RateLimitIdentifiers.ip_identifier(request)

        user_uuid = str(request.state.user_uuid)
        path = helper.get_path()

        return f"{PREFIX_KEY}user:{user_uuid}:{path}"

    @staticmethod
    async def api_key_identifier(request: Request) -> str:
        """
        سطح حساسیت: بسیار بالا
        محدودیت بر اساس API Key
        """
        helper = RequestHelper(request)

        # بررسی انواع مختلف API Key
        api_key = (
            helper.get_header("x-api-key")
            or helper.get_bearer_token()
            or helper.get_query_params().get("api_key")
        )
        path = helper.get_path()

        if not api_key:
            # استفاده از IP به عنوان fallback
            return await RateLimitIdentifiers.ip_identifier(request)

        api_key_hash = RateLimitIdentifiers.hash_sensitive_data(api_key, 12)
        return f"{PREFIX_KEY}api_key:{api_key_hash}:{path}"

    @staticmethod
    async def body_input_value_identifier(
        request: Request, input_key: str, ignore_missed_key: bool = False
    ) -> str:
        """
        سطح حساسیت: بسیار بالا
        محدودیت بر اساس مقدار خاص در body
        """
        helper = RequestHelper(request)

        try:
            json_payload = await helper.get_json_body()
            if not json_payload:
                if ignore_missed_key:
                    return f"{PREFIX_KEY}body_value:{RateLimitIdentifiers.generate_random_identifier()}:{helper.get_path()}"
                raise BadRequestException("Invalid JSON payload for rate limit")

        except Exception:
            if ignore_missed_key:
                return f"{PREFIX_KEY}body_value:{RateLimitIdentifiers.generate_random_identifier()}:{helper.get_path()}"
            raise BadRequestException("Invalid JSON payload for rate limit")

        value = json_payload.get(input_key)
        ip = helper.get_client_ip()
        path = helper.get_path()

        if ip in WHITELIST_IPS or (ignore_missed_key and value is None):
            value = RateLimitIdentifiers.generate_random_identifier()

        if not value:
            raise BadRequestException(
                f"Rate limit error: missing required field '{input_key}'"
            )

        value_hash = RateLimitIdentifiers.hash_sensitive_data(str(value), 12)
        return f"{PREFIX_KEY}body_value:{value_hash}:{path}"

    @staticmethod
    async def composite_identifier(request: Request) -> str:
        """
        سطح حساسیت: حداکثر
        ترکیب چندین شناسه برای محدودیت بسیار سخت
        """
        helper = RequestHelper(request)

        ip = helper.get_client_ip()
        user_agent = helper.get_user_agent()
        device_id = helper.get_header("x-device-id")
        session_id = helper.get_cookie("session_id")
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        # ترکیب همه شناسه ها
        composite_string = f"{ip}:{user_agent}:{device_id}:{session_id}"
        composite_hash = RateLimitIdentifiers.hash_sensitive_data(composite_string, 16)

        return f"{PREFIX_KEY}composite:{composite_hash}:{path}"

    # ========== Advanced Identifiers ==========

    @staticmethod
    async def fingerprint_identifier(request: Request) -> str:
        """
        شناسایی بر اساس Browser Fingerprint
        """
        helper = RequestHelper(request)

        fingerprint_data = {
            "user_agent": helper.get_user_agent(),
            "accept": helper.get_header("accept"),
            "accept_language": helper.get_accept_language(),
            "accept_encoding": helper.get_accept_encoding(),
            "connection": helper.get_header("connection"),
            "upgrade_insecure_requests": helper.get_header("upgrade-insecure-requests"),
            "sec_fetch_dest": helper.get_header("sec-fetch-dest"),
            "sec_fetch_mode": helper.get_header("sec-fetch-mode"),
            "sec_fetch_site": helper.get_header("sec-fetch-site"),
            "is_mobile": helper.is_mobile_request(),
            "is_secure": helper.is_secure_request(),
        }

        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        fingerprint_hash = RateLimitIdentifiers.hash_sensitive_data(
            fingerprint_string, 16
        )
        path = helper.get_path()

        return f"{PREFIX_KEY}fingerprint:{fingerprint_hash}:{path}"

    @staticmethod
    async def geo_location_identifier(request: Request) -> str:
        """
        شناسایی بر اساس موقعیت جغرافیایی (از headers)
        """
        helper = RequestHelper(request)

        # Headers مختلف برای geo location
        country = (
            helper.get_header("cf-ipcountry")  # Cloudflare
            or helper.get_header("x-country-code")
            or helper.get_header("geoip-country-code")
            or "unknown"
        )

        city = (
            helper.get_header("cf-ipcity")  # Cloudflare
            or helper.get_header("x-city-name")
            or helper.get_header("geoip-city")
            or "unknown"
        )

        ip = helper.get_client_ip()
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            country = city = RateLimitIdentifiers.generate_random_identifier()

        return f"{PREFIX_KEY}geo:{country}:{city}:{path}"

    @staticmethod
    async def content_based_identifier(request: Request) -> str:
        """
        شناسایی بر اساس نوع محتوا و اندازه درخواست
        """
        helper = RequestHelper(request)

        # content_type = helper.get_content_type()
        content_length = helper.get_content_length() or 0
        method = helper.get_method()
        path = helper.get_path()
        ip = helper.get_client_ip()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        # دسته‌بندی بر اساس نوع محتوا
        content_category = "unknown"
        if helper.is_json_request():
            content_category = "json"
        elif helper.is_form_request():
            content_category = "form"
        elif helper.is_multipart_request():
            content_category = "multipart"

        # دسته‌بندی بر اساس اندازه
        size_category = "small"
        if content_length > 1024 * 1024:  # > 1MB
            size_category = "large"
        elif content_length > 1024 * 10:  # > 10KB
            size_category = "medium"

        identifier_data = f"{ip}:{method}:{content_category}:{size_category}"
        identifier_hash = RateLimitIdentifiers.hash_sensitive_data(identifier_data, 12)

        return f"{PREFIX_KEY}content:{identifier_hash}:{path}"

    @staticmethod
    async def time_based_identifier(
        request: Request, time_window_minutes: int = 60
    ) -> str:
        """
        شناسایی بر اساس بازه زمانی
        """
        import datetime

        helper = RequestHelper(request)
        ip = helper.get_client_ip()
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        # محاسبه بازه زمانی
        current_time = datetime.datetime.now()
        time_slot = current_time.replace(
            minute=(current_time.minute // time_window_minutes) * time_window_minutes,
            second=0,
            microsecond=0,
        )
        time_key = time_slot.strftime("%Y%m%d_%H%M")

        return f"{PREFIX_KEY}time:{ip}:{time_key}:{path}"

    @staticmethod
    async def referrer_based_identifier(request: Request) -> str:
        """
        شناسایی بر اساس referrer
        """
        helper = RequestHelper(request)

        ip = helper.get_client_ip()
        referrer = helper.get_referrer()
        path = helper.get_path()

        if ip in WHITELIST_IPS:
            ip = RateLimitIdentifiers.generate_random_identifier()

        # استخراج domain از referrer
        referrer_domain = "direct"
        if referrer:
            try:
                from urllib.parse import urlparse

                parsed = urlparse(referrer)
                referrer_domain = parsed.netloc or "unknown"
            except Exception:
                referrer_domain = "invalid"

        referrer_hash = RateLimitIdentifiers.hash_sensitive_data(referrer_domain, 8)

        return f"{PREFIX_KEY}referrer:{ip}:{referrer_hash}:{path}"

    # ========== Utility Functions ==========

    @staticmethod
    async def get_identifier_by_sensitivity(
        request: Request, sensitivity_level: int
    ) -> str:
        """
        انتخاب identifier بر اساس سطح حساسیت
        1: پایین ترین حساسیت
        12: بالاترین حساسیت
        """
        if sensitivity_level <= 1:
            return await RateLimitIdentifiers.global_identifier(request)
        elif sensitivity_level <= 2:
            return await RateLimitIdentifiers.endpoint_identifier(request)
        elif sensitivity_level <= 3:
            return await RateLimitIdentifiers.ip_identifier(request)
        elif sensitivity_level <= 4:
            return await RateLimitIdentifiers.geo_location_identifier(request)
        elif sensitivity_level <= 5:
            return await RateLimitIdentifiers.referrer_based_identifier(request)
        elif sensitivity_level <= 6:
            return await RateLimitIdentifiers.ip_user_agent_identifier(request)
        elif sensitivity_level <= 7:
            return await RateLimitIdentifiers.content_based_identifier(request)
        elif sensitivity_level <= 8:
            return await RateLimitIdentifiers.fingerprint_identifier(request)
        elif sensitivity_level <= 9:
            return await RateLimitIdentifiers.ip_user_agent_device_id_identifier(
                request
            )
        elif sensitivity_level <= 10:
            return await RateLimitIdentifiers.session_identifier(request)
        elif sensitivity_level <= 11:
            return await RateLimitIdentifiers.api_key_identifier(request)
        else:  # sensitivity_level >= 12
            return await RateLimitIdentifiers.composite_identifier(request)

    @staticmethod
    async def get_multi_level_identifier(request: Request, levels: list) -> str:
        """
        ترکیب چندین identifier برای محدودیت چندسطحه
        """
        helper = RequestHelper(request)
        path = helper.get_path()

        identifiers = []
        for level in levels:
            identifier = await RateLimitIdentifiers.get_identifier_by_sensitivity(
                request, level
            )
            identifiers.append(
                identifier.replace(f"{PREFIX_KEY}", "").replace(f":{path}", "")
            )

        combined = ":".join(identifiers)
        combined_hash = RateLimitIdentifiers.hash_sensitive_data(combined, 20)

        return f"{PREFIX_KEY}multi:{combined_hash}:{path}"


# ========== RequestHelper Integration Example ==========


# ========== Example Usage ==========
"""
# در FastAPI endpoint:

from fastapi import FastAPI, Request, Depends
from fastapi_limiter.depends import RateLimiter

app = FastAPI()

@app.post("/api/login")
async def login(
    request: Request,
    ratelimit: bool = Depends(RateLimiter(
        times=5, 
        seconds=300, 
        identifier=ip_user_agent_identifier
    ))
):
    # Login logic here
    pass

@app.post("/api/sensitive-action")
async def sensitive_action(
    request: Request,
    ratelimit: bool = Depends(RateLimiter(
        times=1, 
        seconds=60, 
        identifier=composite_identifier
    ))
):
    # Sensitive action logic here
    pass

# استفاده از body value identifier:
@app.post("/api/verify-phone")
async def verify_phone(
    request: Request,
    ratelimit: bool = Depends(RateLimiter(
        times=3, 
        seconds=3600, 
        identifier=lambda req: body_input_value_identifier(req, "phone_number")
    ))
):
    # Phone verification logic here
    pass

# استفاده از multi-level identifier:
@app.post("/api/critical-action")
async def critical_action(
    request: Request,
    ratelimit: bool = Depends(RateLimiter(
        times=2, 
        seconds=3600, 
        identifier=lambda req: get_multi_level_identifier(req, [5, 8, 10])
    ))
):
    # Critical action logic here
    pass
"""


class RateLimit(RateLimiter):
    async def __call__(self, request: Request, response: Response):
        if (
            not configs.DEBUG
            or NO_RATE_LIMIT_TAG in request.scope.get("route").tags  # type : ignore
        ):
            return
        await super().__call__(request, response)


DEFAULT_LIMIT_DEPENDENCY = RateLimit(
    times=3,
    seconds=1,
    identifier=RateLimitIdentifiers.ip_user_agent_device_id_identifier,
)
