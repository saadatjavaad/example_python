import sys
import os

from fastapi import Request


def show_python_paths():
    """
    نمایش فرمت‌شده تمام مسیرهای موجود در sys.path پایتون
    """
    print("=" * 60)
    print(f"Current Working Directory (CWD): {os.getcwd()}")
    print("=" * 60)
    print("List of Python Search Paths (sys.path):")

    for index, path in enumerate(sys.path, start=1):
        # اگر مسیر خالی بود، به معنی پوشه فعلی اجرای برنامه است
        display_path = path if path != "" else "."
        print(f" [{index}] {display_path}")

    print("=" * 60)


def get_current_user_id(request: Request) -> int:
    """
    استخراج user_id عددی از request.state.user
    (که توسط AuthMiddleware از روی session ردیس ست شده است)
    """

    return int(request.state.user["user_id"])
