from typing import Any, Optional
from fastapi import Request


class RequestHelper:
    """کلاس کمکی برای عملیات رایج روی Request در FastAPI"""

    def __init__(self, request: Request):
        self.request = request

    def get_client_ip(self) -> str:
        """استخراج IP کلاینت"""
        forwarded_for = self.request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = self.request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return self.request.client.host if self.request.client else "unknown"

    def get_user_agent(self) -> str:
        """استخراج User-Agent"""
        return self.request.headers.get("user-agent", "")

    def get_referrer(self) -> str:
        """استخراج Referer"""
        return self.request.headers.get("referer", "")

    def get_bearer_token(self) -> Optional[str]:
        """استخراج Bearer Token"""
        auth_header = self.request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None

    def get_header(self, name: str, default: str = "") -> str:
        """استخراج یک Header خاص"""
        return self.request.headers.get(name.lower(), default)

    def get_cookie(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """استخراج Cookie"""
        return self.request.cookies.get(name, default)

    def get_path(self) -> str:
        """استخراج Path"""
        return self.request.url.path

    def get_method(self) -> str:
        """استخراج HTTP Method"""
        return self.request.method

    def get_content_type(self) -> str:
        """استخراج Content-Type"""
        return self.request.headers.get("content-type", "")

    def get_content_length(self) -> int:
        """استخراج Content-Length"""
        try:
            return int(self.request.headers.get("content-length", "0"))
        except ValueError:
            return 0

    def get_accept_language(self) -> str:
        """استخراج Accept-Language"""
        return self.request.headers.get("accept-language", "")

    def get_accept_encoding(self) -> str:
        """استخراج Accept-Encoding"""
        return self.request.headers.get("accept-encoding", "")

    def get_query_params(self) -> dict[Any, Any]:
        """استخراج Query Parameters"""
        return dict(self.request.query_params)

    def is_json_request(self) -> bool:
        """بررسی JSON Request"""
        content_type = self.get_content_type()
        return "application/json" in content_type.lower()

    def is_form_request(self) -> bool:
        """بررسی Form Request"""
        content_type = self.get_content_type()
        return "application/x-www-form-urlencoded" in content_type.lower()

    def is_multipart_request(self) -> bool:
        """بررسی Multipart Request"""
        content_type = self.get_content_type()
        return "multipart/form-data" in content_type.lower()

    def is_mobile_request(self) -> bool:
        """بررسی درخواست از موبایل"""
        user_agent = self.get_user_agent().lower()
        mobile_keywords = ["mobile", "android", "iphone", "ipad", "tablet"]
        return any(keyword in user_agent for keyword in mobile_keywords)

    def is_secure_request(self) -> bool:
        """بررسی HTTPS"""
        return self.request.url.scheme == "https"

    async def get_json_body(self) -> Optional[dict]:
        """استخراج JSON Body"""
        if not self.is_json_request():
            return None

        try:
            return await self.request.json()
        except Exception:
            return None
