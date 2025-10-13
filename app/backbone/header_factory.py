class HeaderFactory:
    @staticmethod
    def video_download_headers(
        start: int,
        end: int,
        file_size: int,
        content_length: int,
        filename: str,
        filetype: str = "mp4",
        mime_type: str = "video/mp4",
    ) -> dict:
        if mime_type is None:
            # تعیین نوع MIME بر اساس پسوند فایل
            mime_map = {
                "mp4": "video/mp4",
                "webm": "video/webm",
                "mov": "video/quicktime",
                "avi": "video/x-msvideo",
                "mkv": "video/x-matroska",
            }
            mime_type = mime_map.get(filetype.lower(), "application/octet-stream")
        return {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": mime_type,
            "Content-Disposition": f'attachment; filename="{filename}.{filetype}"',
        }

    @staticmethod
    def json_response_headers() -> dict:
        return {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
        }

    @staticmethod
    def pdf_download_headers(filename: str) -> dict:
        return {
            "Content-Type": "application/pdf",
            "Content-Disposition": f'attachment; filename="{filename}.pdf"',
        }

    @staticmethod
    def image_response_headers(image_type: str = "jpeg") -> dict:
        return {
            "Content-Type": f"image/{image_type}",
            "Cache-Control": "public, max-age=86400",
        }

    @staticmethod
    def plain_text_headers() -> dict:
        return {
            "Content-Type": "text/plain; charset=utf-8",
        }
