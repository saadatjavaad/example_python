class MemoryUnit:
    """واحدهای حافظه به بایت، به صورت ثابت و قابل استفاده در کل پروژه."""

    BYTE: int = 1
    KB: int = 1024 * BYTE
    MB: int = 1024 * KB
    GB: int = 1024 * MB
    TB: int = 1024 * GB

    @classmethod
    def format(cls, size_in_bytes: int) -> str:
        """تبدیل بایت به رشته‌ی خوانا مثل '2.5 MB'"""
        if size_in_bytes < cls.KB:
            return f"{size_in_bytes} B"
        elif size_in_bytes < cls.MB:
            return f"{size_in_bytes / cls.KB:.2f} KB"
        elif size_in_bytes < cls.GB:
            return f"{size_in_bytes / cls.MB:.2f} MB"
        elif size_in_bytes < cls.TB:
            return f"{size_in_bytes / cls.GB:.2f} GB"
        else:
            return f"{size_in_bytes / cls.TB:.2f} TB"
