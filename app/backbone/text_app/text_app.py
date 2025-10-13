import json
from enum import Enum
from pathlib import Path

# Load translations from JSON files
def load_translations(file_name: str) -> dict:
    file_path = Path(__file__).parent / file_name
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

en = load_translations("en.json")
fa = load_translations("fa.json")


class Language(Enum):
    FA = fa
    EN = en


class TextApp:
    @staticmethod
    def get(key: str, *argoman, lang: Language = Language.EN, **kargoman) -> str:
        """
        دریافت متن براساس زبان، کلید و جایگزینی مقادیر پویا
        :param key: نام کلید
        :param argoman: ورودی پوزیشنی برای جایگزینی
        :param lang: زبان (پیش‌فرض EN)
        :param kargoman: ورودی کلیدی برای جایگزینی
        """
        strings = lang.value
        text = strings.get(key, key)  # اگر کلید نبود، خودش برگرده

        if not isinstance(text, str):
            return key

        try:
            return text.format(*argoman, **kargoman)
        except Exception:
            return text
