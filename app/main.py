if __name__ == "__main__":
    import asyncio

    async def main():
        import os

        def run_dev() -> None:
            """اجرای Uvicorn در حالت توسعه با reload"""
            import uvicorn

            uvicorn.run("bootstrap.api:app", host="127.0.0.1", port=8001, reload=True)

        def run_prod() -> None:
            """اجرای Gunicorn با UvicornWorker در حالت Production"""
            import multiprocessing

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
            os.execvp("gunicorn", cmd)

        from backbone.configs import configs

        if configs.DEBUG:
            print("🚀 Starting in development mode with reload=True")
            run_dev()
        else:
            print("🚀 Starting in production mode with Gunicorn")
            run_prod()

    asyncio.run(main())
