import multiprocessing
import os

import uvicorn
from backbone.configs import configs


def run_dev() -> None:
    """اجرای Uvicorn در حالت توسعه و مناسب برای Debug."""
    print("🚀 Starting in development mode")
    print("🐞 Debug mode: Breakpoints enabled")
    print("📍 Server: http://127.0.0.1:8001")

    uvicorn.run(
        "bootstrap.api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
    )


def run_prod() -> None:
    """اجرای Gunicorn با UvicornWorker در حالت Production."""

    workers: int = multiprocessing.cpu_count() * 2 + 1

    cmd: list[str] = [
        "gunicorn",
        "bootstrap.api:app",
        "-w",
        str(workers),
        "-k",
        "uvicorn.workers.UvicornWorker",
        "--bind",
        "0.0.0.0:8080",
    ]

    print("🚀 Starting in production mode with Gunicorn")
    print(f"👷 Workers: {workers}")
    print("📍 Server: http://0.0.0.0:8080")

    os.execvp("gunicorn", cmd)


def main() -> None:
    if configs.DEBUG:
        run_dev()
    else:
        run_prod()


if __name__ == "__main__":
    main()
