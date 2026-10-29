# app/services/file_storage.py

from pathlib import Path
from typing import BinaryIO
from uuid import uuid4


class FileStorageService:

    def __init__(
        self,
        storage_dir: str = "storage",
        base_url: str = "/files",
    ):
        self.storage_dir = Path(storage_dir)
        self.base_url = base_url.rstrip("/")

        # ساخت پوشه اصلی در صورت عدم وجود
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        file: BinaryIO,
        folder: str,
        filename: str,
    ) -> str:
        """
        فایل را ذخیره می‌کند و URL آن را برمی‌گرداند.
        """

        folder_path = self.storage_dir / folder

        # ساخت پوشه
        folder_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        # جلوگیری از نام‌های تکراری
        extension = Path(filename).suffix
        generated_name = f"{uuid4().hex}{extension}"

        file_path = folder_path / generated_name

        # ذخیره فایل
        with file_path.open("wb") as destination:
            while chunk := file.read(1024 * 1024):
                destination.write(chunk)

        # آدرس قابل استفاده توسط API
        return f"{self.base_url}/{folder}/{generated_name}"

    def delete(self, file_url: str) -> bool:
        """
        فایل را با استفاده از URL حذف می‌کند.
        """

        relative_path = file_url.removeprefix(self.base_url).lstrip("/")

        file_path = self.storage_dir / relative_path

        if not file_path.exists():
            return False

        if not file_path.is_file():
            return False

        file_path.unlink()

        return True

    def exists(self, file_url: str) -> bool:
        """
        بررسی وجود فایل.
        """

        relative_path = file_url.removeprefix(self.base_url).lstrip("/")

        file_path = self.storage_dir / relative_path

        return file_path.is_file()

    def get_path(self, file_url: str) -> Path:
        """
        مسیر واقعی فایل روی سرور را برمی‌گرداند.
        """

        relative_path = file_url.removeprefix(self.base_url).lstrip("/")

        return self.storage_dir / relative_path
