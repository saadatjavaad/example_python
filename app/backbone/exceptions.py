import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Optional
from backbone.text_app.text_app import TextApp


logger = logging.getLogger(__name__)


class BaseHttpException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str],
        location: Optional[list[str]] = list(),
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.location = location


class Exception404(BaseHttpException):  # Not Found
    def __init__(self, detail: str = TextApp.get("resource_not_found")) -> None:
        super().__init__(status_code=404, detail=detail)


class Exception403(BaseHttpException):  # Access Denied
    def __init__(self, detail: str = TextApp.get("access_denied")) -> None:
        super().__init__(status_code=403, detail=detail)


class Exception403Forbidden(BaseHttpException):  # Forbidden with scope
    def __init__(
        self,
        detail: Optional[str] = None,
    ):
        super().__init__(status_code=403, detail=detail)


class ApiServiceException(BaseHttpException):  # Dynamic status_code
    def __init__(
        self,
        status_code: int,
        detail: str = TextApp.get("api_service"),
        location: Optional[list[str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, location=location)

    def __str__(self):
        return TextApp.get(
            "ApiServiceException_detail_Status_Code_Resource",
            self.detail,
            self.status_code,
            self.resource,
        )


# --- 4xx Client Errors ---
class Exception400(BaseHttpException):  # Bad Request
    def __init__(self, detail: str = "Bad request", location: list[str] = list()):
        super().__init__(status_code=400, detail=detail, location=location)


class Exception400Integrity(BaseHttpException):  # Integrity Error
    def __init__(self, detail: str = "Integrity error"):
        super().__init__(status_code=400, detail=detail)


class Exception400AlreadyExist(BaseHttpException):  # Integrity Error
    def __init__(self, detail: str = "already exists"):
        super().__init__(status_code=400, detail=detail)


class Exception401(BaseHttpException):  # Unauthorized (Unauthenticated)
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=401, detail=detail)


class Exception403Unauthorized(BaseHttpException):  # Forbidden (Unauthorized access)
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail)


class Exception403DomainRestricted(BaseHttpException):  # Domain Restricted
    def __init__(self, domain: Optional[str], detail: str = "Domain restricted"):
        super().__init__(status_code=403, detail=detail)
        self.domain = domain

    def __str__(self):
        return f"{self.detail} - Restricted to domain: {self.domain}"


class Exception405(BaseHttpException):  # Method Not Allowed
    def __init__(self, detail: str = "Method not allowed"):
        super().__init__(status_code=405, detail=detail)


class Exception406(BaseHttpException):  # Not Acceptable
    def __init__(self, detail: str = "Not acceptable"):
        super().__init__(status_code=406, detail=detail)


class Exception408(BaseHttpException):  # Request Timeout
    def __init__(self, detail: str = "Request timeout"):
        super().__init__(status_code=408, detail=detail)


class Exception409(BaseHttpException):  # Conflict
    def __init__(self, detail: str = "Conflict - Resource already exists"):
        super().__init__(status_code=409, detail=detail)


class Exception410(BaseHttpException):  # Gone
    def __init__(self, detail: str = "Resource is gone"):
        super().__init__(status_code=410, detail=detail)


class Exception413(BaseHttpException):  # Payload Too Large
    def __init__(self, detail: str = "Payload too large"):
        super().__init__(status_code=413, detail=detail)


class Exception415(BaseHttpException):  # Unsupported Media Type
    def __init__(self, detail: str = "Unsupported media type"):
        super().__init__(status_code=415, detail=detail)


class Exception422(BaseHttpException):  # Unprocessable Entity
    def __init__(
        self, detail: str = "Unprocessable request", location: list[str] = list()
    ):
        super().__init__(status_code=422, detail=detail, location=location)


class Exception429(BaseHttpException):  # Too Many Requests
    def __init__(self, detail: str = "Too many requests (rate limit exceeded)"):
        super().__init__(status_code=429, detail=detail)


# --- 5xx Server Errors ---
class Exception500(BaseHttpException):  # Internal Server Error
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)


class Exception501(BaseHttpException):  # Not Implemented
    def __init__(self, detail: str = "Not implemented"):
        super().__init__(status_code=501, detail=detail)


class Exception502(BaseHttpException):  # Bad Gateway
    def __init__(self, detail: str = "Bad gateway"):
        super().__init__(status_code=502, detail=detail)


class Exception503(BaseHttpException):  # Service Unavailable
    def __init__(self, detail: str = "Service unavailable"):
        super().__init__(status_code=503, detail=detail)


class Exception503SMS(BaseHttpException):  # Service Unavailable
    def __init__(
        self, detail: str = "SMS service unavailable. Please try again later."
    ):
        super().__init__(status_code=503, detail=detail)


class Exception504(BaseHttpException):  # Gateway Timeout
    def __init__(self, detail: str = "Gateway timeout"):
        super().__init__(status_code=504, detail=detail)


class Exception507(BaseHttpException):  # Insufficient Storage
    def __init__(self, detail: str = "Insufficient storage"):
        super().__init__(status_code=507, detail=detail)


class Exception511(BaseHttpException):  # Network Authentication Required
    def __init__(self, detail: str = "Network authentication required"):
        super().__init__(status_code=511, detail=detail)


# --- Additional 20 HTTP Exceptions ---


class Exception402(BaseHttpException):  # Payment Required
    def __init__(self, detail: str = "Payment required"):
        super().__init__(status_code=402, detail=detail)


class Exception407(BaseHttpException):  # Proxy Authentication Required
    def __init__(self, detail: str = "Proxy authentication required"):
        super().__init__(status_code=407, detail=detail)


class Exception411(BaseHttpException):  # Length Required
    def __init__(self, detail: str = "Content-Length header required"):
        super().__init__(status_code=411, detail=detail)


class Exception412(BaseHttpException):  # Precondition Failed
    def __init__(self, detail: str = "Precondition failed"):
        super().__init__(status_code=412, detail=detail)


class Exception414(BaseHttpException):  # URI Too Long
    def __init__(self, detail: str = "Request URI too long"):
        super().__init__(status_code=414, detail=detail)


class Exception416(BaseHttpException):  # Range Not Satisfiable
    def __init__(self, detail: str = "Requested range not satisfiable"):
        super().__init__(status_code=416, detail=detail)


class Exception417(BaseHttpException):  # Expectation Failed
    def __init__(self, detail: str = "Expectation failed"):
        super().__init__(status_code=417, detail=detail)


class Exception418(BaseHttpException):  # I'm a teapot (fun Easter egg RFC)
    def __init__(self, detail: str = "I'm a teapot"):
        super().__init__(status_code=418, detail=detail)


class Exception421(BaseHttpException):  # Misdirected Request
    def __init__(self, detail: str = "Misdirected request"):
        super().__init__(status_code=421, detail=detail)


class Exception423(BaseHttpException):  # Locked
    def __init__(self, detail: str = "Resource is locked"):
        super().__init__(status_code=423, detail=detail)


class Exception424(BaseHttpException):  # Failed Dependency
    def __init__(self, detail: str = "Failed dependency"):
        super().__init__(status_code=424, detail=detail)


class Exception425(BaseHttpException):  # Too Early
    def __init__(self, detail: str = "Too early to process request"):
        super().__init__(status_code=425, detail=detail)


class Exception426(BaseHttpException):  # Upgrade Required
    def __init__(self, detail: str = "Upgrade required"):
        super().__init__(status_code=426, detail=detail)


class Exception428(BaseHttpException):  # Precondition Required
    def __init__(self, detail: str = "Precondition required"):
        super().__init__(status_code=428, detail=detail)


class Exception431(BaseHttpException):  # Request Header Fields Too Large
    def __init__(self, detail: str = "Request header fields too large"):
        super().__init__(status_code=431, detail=detail)


class Exception451(BaseHttpException):  # Unavailable For Legal Reasons
    def __init__(self, detail: str = "Unavailable due to legal reasons"):
        super().__init__(status_code=451, detail=detail)


# --- Extra 5xx Errors ---
class Exception506(BaseHttpException):  # Variant Also Negotiates
    def __init__(self, detail: str = "Variant also negotiates"):
        super().__init__(status_code=506, detail=detail)


class Exception508(BaseHttpException):  # Loop Detected
    def __init__(self, detail: str = "Loop detected"):
        super().__init__(status_code=508, detail=detail)


class Exception510(BaseHttpException):  # Not Extended
    def __init__(self, detail: str = "Not extended"):
        super().__init__(status_code=510, detail=detail)


class Exception599(BaseHttpException):  # Network Connect Timeout Error (custom)
    def __init__(self, detail: str = "Network connect timeout error"):
        super().__init__(status_code=599, detail=detail)


# --- OTP related Exceptions ---


class Exception400OTPExpired(BaseHttpException):  # OTP Expired
    def __init__(self, detail: str = "OTP has expired"):
        super().__init__(status_code=400, detail=detail)


class Exception400OTPInvalid(BaseHttpException):  # Invalid OTP
    def __init__(self, detail: str = "Invalid OTP code"):
        super().__init__(status_code=400, detail=detail)


class Exception429OTPAttemptsExceeded(BaseHttpException):  # Too many wrong attempts
    def __init__(self, detail: str = "Maximum OTP attempts exceeded"):
        super().__init__(status_code=429, detail=detail)


class Exception404OTPNotRequested(BaseHttpException):  # User never requested OTP
    def __init__(self, detail: str = "OTP request not found"):
        super().__init__(status_code=404, detail=detail)


class Exception502OTPDeliveryFailed(BaseHttpException):  # Failed to send OTP
    def __init__(self, detail: str = "Failed to deliver OTP (SMS/Email error)"):
        super().__init__(status_code=502, detail=detail)


# فرض: BaseHttpException و Exception422 از قبل تعریف شده‌اند
# از متن شما استفاده شد
class Errhandler:
    """
    کلاس مدیریت خطاها، شامل متدهای استاتیک
    """

    @staticmethod
    async def validation_error(request: Request, exc: Any) -> JSONResponse:
        """
        مدیریت خطاهای اعتبارسنجی (422)
        """
        # devlog(exc)  # اگر نیاز به لاگ دارید
        errors = [
            {
                "field": ".".join([str(loc) for loc in err["loc"] if loc != "body"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422, content={"status": "error", "errors": errors}
        )

    @staticmethod
    async def general_error(request: Request, exc: Any) -> JSONResponse:
        """
        مدیریت سایر Exception ها و خطاهای HTTP
        """
        # devlog(exc)  # لاگ توسعه
        # مدیریت BaseHttpException خاص
        if hasattr(exc, "status_code"):
            code = getattr(exc, "status_code", 500)
            message = getattr(exc, "detail", str(exc))
        else:
            code = 500
            message = str(exc)

        # بررسی هدر origin برای CORS
        origin = request.headers.get("origin")
        headers = {}
        if origin:
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }

        return JSONResponse(
            status_code=code,
            content={"status": "error", "message": message},
            headers=headers if headers else None,
        )


# """
# Custom HTTP Exceptions for API.

# Usage guide for when to raise each exception:

# - NotFoundException (404): When a requested resource (user, item, etc.) does not exist.
# - AccessDeniedException (403): When the user is authenticated but does not have permission to access the resource.
# - ForbiddenException (403): When access is forbidden for a specific scope or resource.
# - ApiServiceException (Custom code): When an internal or external API service fails or returns an error.
# - UnauthorizedException (403): When the user tries to access a resource without valid authorization (e.g., invalid token).
# - UnauthenticatedException (401): When authentication is required but missing (e.g., user not logged in).
# - ConflictException (409): When trying to create or update a resource that already exists (e.g., duplicate email).
# - UnprocessableRequestException (422): When the request data is semantically invalid or cannot be processed.
# - IntegrityException (400): When a database integrity error occurs (e.g., foreign key constraint violation).
# - BadRequestException (400): When the request data is invalid, malformed, or missing required fields.
# - ServerErrorException (500): For unexpected server-side errors.
# - DomainRestrictedException (403): When access is restricted to a specific domain or environment.

# Exception handlers:
# - http_exception_handler: Handles known BaseHttpException types and returns a proper JSON response.
# - general_exception_handler: Captures unexpected exceptions, reports them to Sentry, and returns a generic error message to the client.
# """
