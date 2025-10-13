from typing import Optional
import aiohttp
import aiofiles


import os


class ApiClient:
    def __init__(
        self, base_url: Optional[str] = None, timeout=10, headers: dict[str, str] = {}
    ):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = headers

    def set_headers(self, headers: dict):
        self.headers.update(headers)

    async def _request(
        self, method, url, params=None, data=None, json=None, files=None
    ):
        full_url = f"{self.base_url}{url}" if self.base_url else url
        async with aiohttp.ClientSession(
            timeout=self.timeout, headers=self.headers
        ) as session:
            if files:
                form = aiohttp.FormData()
                for key, file_info in files.items():
                    form.add_field(
                        key,
                        file_info["file"],
                        filename=file_info.get(
                            "filename", os.path.basename(file_info["file"].name)
                        ),
                        content_type=file_info.get(
                            "content_type", "application/octet-stream"
                        ),
                    )
                data = form

            async with session.request(
                method, full_url, params=params, data=data, json=json
            ) as resp:
                return {
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body": await resp.text(),
                }

    async def get(self, url, params=None):
        return await self._request("GET", url, params=params)

    async def post(self, url, data=None, json=None):
        return await self._request("POST", url, data=data, json=json)

    async def put(self, url, data=None, json=None):
        return await self._request("PUT", url, data=data, json=json)

    async def delete(self, url, params=None):
        return await self._request("DELETE", url, params=params)

    # ارسال یک فایل
    async def upload_file(self, url: str, file_path: str, field_name: str = "file"):
        async with aiofiles.open(file_path, "rb") as f:
            return await self._request("POST", url, files={field_name: {"file": f}})

    # ارسال چند فایل
    async def upload_files(self, url: str, files: dict[str, str]):
        """
        files: دیکشنری به شکل {field_name: file_path}
        """
        files_dict = {}
        import aiofiles

        for field_name, path in files.items():
            f = await aiofiles.open(path, "rb")
            files_dict[field_name] = {"file": f}
        return await self._request("POST", url, files=files_dict)

    async def download_file(self, url: str, dest_path: str, params=None):
        """
        دانلود فایل بدون پکیج اضافی
        """
        full_url = f"{self.base_url}{url}" if self.base_url else url
        async with aiohttp.ClientSession(
            timeout=self.timeout, headers=self.headers
        ) as session:
            async with session.get(full_url, params=params) as resp:
                resp.raise_for_status()
                with open(dest_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        f.write(chunk)
        return {"status": resp.status, "path": dest_path}


# --- مثال استفاده ---
async def main():
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    client.set_headers({"Content-Type": "application/json"})

    # درخواست GET
    response = await client.get("/posts", params={"userId": 1})
    print(response)

    # درخواست POST
    response = await client.post(
        "/posts", json={"title": "test", "body": "hello", "userId": 1}
    )
    print(response)


# asyncio.run(main())
