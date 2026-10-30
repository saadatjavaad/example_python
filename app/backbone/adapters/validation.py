import re
from typing import Callable, Any, List


class ValidationError(Exception):
    pass


class Validator:
    def __init__(self):
        self.rules: List[tuple[Callable[[Any], bool], str]] = []

    def add_rule(self, rule: Callable[[Any], bool], message: str):
        """Add a custom rule."""
        self.rules.append((rule, message))
        return self

    def validate(self, value: Any):
        """Run all rules against the given value."""
        errors = []
        for rule, message in self.rules:
            if not rule(value):
                errors.append(message)
        if errors:
            raise ValidationError(errors)
        return True

    # Built-in rules
    def required(self):
        return self.add_rule(
            lambda v: v is not None and v != "", "This field is required"
        )

    def min_length(self, length: int):
        return self.add_rule(
            lambda v: isinstance(v, str) and len(v) >= length,
            f"Length must be at least {length} characters",
        )

    def max_length(self, length: int):
        return self.add_rule(
            lambda v: isinstance(v, str) and len(v) <= length,
            f"Length must be at most {length} characters",
        )

    def regex(self, pattern: str, message: str = "Invalid format"):
        regex_compiled = re.compile(pattern)
        return self.add_rule(
            lambda v: isinstance(v, str) and bool(regex_compiled.match(v)), message
        )

    def is_number(self):
        return self.add_rule(lambda v: str(v).isdigit(), "Must contain only digits")

    def email(self):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return self.regex(pattern, "Must be a valid email address")


class CommonValidators:
    """Static factory methods for common validators."""

    @staticmethod
    def username():
        return Validator().required().min_length(3).max_length(20)

    @staticmethod
    def email():
        return Validator().required().email()

    @staticmethod
    def password():
        return (
            Validator()
            .required()
            .min_length(8)
            .max_length(64)
            .regex(r".*[A-Z].*", "Must contain at least one uppercase letter")
            .regex(r".*[a-z].*", "Must contain at least one lowercase letter")
            .regex(r".*\d.*", "Must contain at least one digit")
            .regex(
                r".*[@$!%*?&].*",
                "Must contain at least one special character (@$!%*?&)",
            )
        )

    @staticmethod
    def age():
        return Validator().add_rule(
            lambda v: isinstance(v, int) and v >= 18, "Must be at least 18 years old"
        )

    @staticmethod
    def phone_number():
        return Validator().regex(r"^\+?\d{10,15}$", "Must be a valid phone number")


# --------------------
# Example usage
# --------------------

try:
    CommonValidators.username().validate("ali")
    print("Username is valid ✅")
except ValidationError as e:
    print("Username error:", e)

try:
    CommonValidators.password().validate("WeakPass")
except ValidationError as e:
    print("Password error:", e)

try:
    CommonValidators.email().validate("test@example.com")
    print("Email is valid ✅")
except ValidationError as e:
    print("Email error:", e)
