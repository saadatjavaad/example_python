import hashlib
from backbone.helpers.str import StrHelper


class HashHelpers:
    @staticmethod
    def md5_hash(text: str) -> str:
        """محاسبه هش MD5 از یک رشته"""
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def sha1_hash(text: str) -> str:
        """محاسبه هش SHA1 از یک رشته"""
        return hashlib.sha1(text.encode()).hexdigest()

    @staticmethod
    def sha224_hash(text: str) -> str:
        """محاسبه هش SHA224 از یک رشته"""
        return hashlib.sha224(text.encode()).hexdigest()

    @staticmethod
    def sha256_hash(text: str) -> str:
        """محاسبه هش SHA256 از یک رشته"""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def sha384_hash(text: str) -> str:
        """محاسبه هش SHA384 از یک رشته"""
        return hashlib.sha384(text.encode()).hexdigest()

    @staticmethod
    def sha512_hash(text: str) -> str:
        """محاسبه هش SHA512 از یک رشته"""
        return hashlib.sha512(text.encode()).hexdigest()

    @staticmethod
    def blake2b_hash(text: str) -> str:
        """محاسبه هش Blake2b از یک رشته"""
        return hashlib.blake2b(text.encode()).hexdigest()

    @staticmethod
    def blake2s_hash(text: str) -> str:
        """محاسبه هش Blake2s از یک رشته"""
        return hashlib.blake2s(text.encode()).hexdigest()

    @staticmethod
    def sha3_224_hash(text: str) -> str:
        """محاسبه هش SHA3-224 از یک رشته"""
        return hashlib.sha3_224(text.encode()).hexdigest()

    @staticmethod
    def sha3_256_hash(text: str) -> str:
        """محاسبه هش SHA3-256 از یک رشته"""
        return hashlib.sha3_256(text.encode()).hexdigest()

    @staticmethod
    def sha3_384_hash(text: str) -> str:
        """محاسبه هش SHA3-384 از یک رشته"""
        return hashlib.sha3_384(text.encode()).hexdigest()

    @staticmethod
    def sha3_512_hash(text: str) -> str:
        """محاسبه هش SHA3-512 از یک رشته"""
        return hashlib.sha3_512(text.encode()).hexdigest()

    @staticmethod
    def hash(text: str, length: int | None) -> str:
        h: str = HashHelpers.sha3_256_hash(text)
        return StrHelper.chars_until(h, length) if length is not None else h
