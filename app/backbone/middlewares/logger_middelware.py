import json
import time
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.perf_counter()

        # =========================
        # Request Body
        # =========================

        request_body = await request.body()

        async def receive():
            return {
                "type": "http.request",
                "body": request_body,
                "more_body": False,
            }

        request._receive = receive

        content_type = request.headers.get("content-type", "")

        # =========================
        # Request
        # =========================

        print("\n" + "═" * 80)

        print(f"\033[1;36m➡️  {request.method} {request.url.path}\033[0m")

        print(f"\033[90mQuery: {request.url.query}\033[0m")

        print(f"\033[90mContent-Type: {content_type}\033[0m")

        # =========================
        # Request Body Log
        # =========================

        if request_body:

            print("\033[1;33m📥 Request Body:\033[0m")

            if "application/json" in content_type:

                try:

                    body = json.loads(request_body.decode("utf-8"))

                    print(
                        "\033[33m"
                        + json.dumps(
                            body,
                            indent=2,
                            ensure_ascii=False,
                        )
                        + "\033[0m"
                    )

                except (json.JSONDecodeError, UnicodeDecodeError):

                    print(
                        "\033[33m"
                        + request_body.decode(
                            "utf-8",
                            errors="replace",
                        )
                        + "\033[0m"
                    )

            elif "multipart/form-data" in content_type:

                print("\033[33m" "[multipart/form-data - body omitted]" "\033[0m")

            elif "application/x-www-form-urlencoded" in content_type:

                print(
                    "\033[33m"
                    + request_body.decode(
                        "utf-8",
                        errors="replace",
                    )
                    + "\033[0m"
                )

            else:

                print(
                    "\033[33m"
                    + request_body.decode(
                        "utf-8",
                        errors="replace",
                    )
                    + "\033[0m"
                )

        # =========================
        # Execute Request
        # =========================

        try:

            response = await call_next(request)

        except Exception as exc:

            elapsed = (time.perf_counter() - start_time) * 1000

            print(f"\n\033[1;31m❌ EXCEPTION\033[0m")

            print(f"\033[31m" f"{type(exc).__name__}: {exc}" f"\033[0m")

            print(f"\033[90m⏱ {elapsed:.2f} ms\033[0m")

            traceback.print_exc()

            print("═" * 80 + "\n")

            raise

        # =========================
        # Response Body
        # =========================

        response_body = b""

        async for chunk in response.body_iterator:
            response_body += chunk

        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        # =========================
        # Response Log
        # =========================

        elapsed = (time.perf_counter() - start_time) * 1000

        status_color = "\033[1;32m" if response.status_code < 400 else "\033[1;31m"

        print(f"\n{status_color}" f"⬅️  {response.status_code}" f"\033[0m")

        response_content_type = response.headers.get("content-type", "")

        if response_body:

            print("\033[1;35m📤 Response Body:\033[0m")

            if "application/json" in response_content_type:

                try:

                    body = json.loads(response_body.decode("utf-8"))

                    print(
                        "\033[35m"
                        + json.dumps(
                            body,
                            indent=2,
                            ensure_ascii=False,
                        )
                        + "\033[0m"
                    )

                except (json.JSONDecodeError, UnicodeDecodeError):

                    print(
                        response_body.decode(
                            "utf-8",
                            errors="replace",
                        )
                    )

            else:

                print(
                    response_body.decode(
                        "utf-8",
                        errors="replace",
                    )
                )

        print(f"\033[90m⏱ {elapsed:.2f} ms\033[0m")

        print("═" * 80 + "\n")

        return response
