# string_utils.py

import re
from typing import Optional


class StrHelper:
    @staticmethod
    def to_lower(text: str) -> str:
        """تبدیل همه حروف به حروف کوچک"""
        return text.lower()

    @staticmethod
    def to_upper(text: str) -> str:
        """تبدیل همه حروف به حروف بزرگ"""
        return text.upper()

    @staticmethod
    def remove_spaces(text: str) -> str:
        """حذف تمام فاصله‌ها از رشته"""
        return text.replace(" ", "")

    @staticmethod
    def trim(text: str) -> str:
        """حذف فاصله‌های ابتدا و انتهای رشته"""
        return text.strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """جایگزینی چند فاصله متوالی با یک فاصله"""
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def substring(text: str, start: int, length: Optional[int] = None) -> str:
        """برش متن از اندیس start به طول length (اگر طول داده نشود تا انتها)"""
        if length is None:
            return text[start:]
        else:
            return text[start : start + length]

    @staticmethod
    def replace_substring(text: str, old: str, new: str) -> str:
        """جایگزینی تمام قسمت‌های old با new در متن"""
        return text.replace(old, new)

    @staticmethod
    def contains(text: str, substring: str) -> bool:
        """بررسی وجود substring در متن"""
        return substring in text

    @staticmethod
    def count_occurrences(text: str, substring: str) -> int:
        """شمارش تعداد دفعات تکرار substring در متن"""
        return text.count(substring)

    @staticmethod
    def reverse(text: str) -> str:
        """معکوس کردن رشته"""
        return text[::-1]

    @staticmethod
    def is_palindrome(text: str) -> bool:
        """بررسی اینکه آیا رشته پلین‌دروم (قرینه) است یا نه"""
        clean_text = StrHelper.normalize_whitespace(text).replace(" ", "").lower()
        return clean_text == clean_text[::-1]

    @staticmethod
    def substring_from_end(text: str, length: int) -> str:
        """برش n کاراکتر آخر رشته"""
        return text[-length:] if length <= len(text) else text

    @staticmethod
    def substring_before(text: str, delimiter: str) -> str:
        """برش متن قبل از اولین وقوع delimiter"""
        index = text.find(delimiter)
        return text[:index] if index != -1 else text

    @staticmethod
    def substring_after(text: str, delimiter: str) -> str:
        """برش متن بعد از اولین وقوع delimiter"""
        index = text.find(delimiter)
        return text[index + len(delimiter) :] if index != -1 else ""

    @staticmethod
    def substring_between(text: str, start_delim: str, end_delim: str) -> str:
        """برش متن بین دو delimiter (اولین وقوع‌ها)"""
        start_idx = text.find(start_delim)
        end_idx = text.find(end_delim, start_idx + 1)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx + len(start_delim) : end_idx]
        return ""

    @staticmethod
    def split_and_get(text: str, delimiter: str, index: int) -> str:
        """تقسیم رشته با delimiter و گرفتن قسمت indexام"""
        parts = text.split(delimiter)
        if 0 <= index < len(parts):
            return parts[index]
        return ""

    @staticmethod
    def repeat_text(text: str, times: int) -> str:
        """تکرار متن به تعداد times"""
        return text * times

    @staticmethod
    def pad_text(text: str, length: int, pad_char: str = " ") -> str:
        """پرکردن رشته تا طول مشخص با کاراکتر دلخواه (پیش‌فرض فاصله)"""
        if len(text) >= length:
            return text
        return text + pad_char * (length - len(text))

    @staticmethod
    def is_empty(text: str) -> bool:
        """بررسی اینکه رشته خالی یا فقط شامل فاصله است"""
        return len(text.strip()) == 0

    @staticmethod
    def chars_until(text: str, index: int) -> str:
        """برگرداندن کاراکترها از ابتدا تا index (index شامل نمی‌شود)"""
        return text[:index]

    @staticmethod
    def chars_from(text: str, index: int) -> str:
        """برگرداندن کاراکترها از index تا انتها"""
        return text[index:]

    @staticmethod
    def chars_at_odd_indices(text: str) -> str:
        """برگرداندن کاراکترهایی که ایندکس‌شان فرد است"""
        return "".join([c for i, c in enumerate(text) if i % 2 == 1])

    @staticmethod
    def chars_at_even_indices(text: str) -> str:
        """برگرداندن کاراکترهایی که ایندکس‌شان زوج است"""
        return "".join([c for i, c in enumerate(text) if i % 2 == 0])

    @staticmethod
    def chars_at_indices(text: str, indices: list[int]) -> str:
        """برگرداندن کاراکترهای متن در ایندکس‌های مشخص شده در لیست"""
        return "".join([text[i] for i in indices if 0 <= i < len(text)])
