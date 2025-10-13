import inspect
import json
from pprint import pprint
from typing import Any, Type
from colorama import Fore, Style, init

# فعال‌سازی رنگ در ویندوز و لینوکس
init(autoreset=True)


def colored_value(value: Any, default_color: str = Fore.YELLOW) -> str:
    type_colors: dict[Type[Any], str] = {
        int: Fore.LIGHTGREEN_EX,
        float: Fore.LIGHTGREEN_EX,
        str: Fore.RED,
        bool: Fore.LIGHTBLUE_EX,
        type(None): Fore.BLACK,
        list: Fore.BLUE,
        dict: Fore.BLUE,
    }
    return type_colors.get(type(value), default_color)  # type: ignore


def format_value(value: Any, indent: str = "    "):
    """مقدار را به شکل زیبا و رنگی برمی‌گرداند."""
    if isinstance(value, (int, float)):
        return colored_value(value) + repr(value)
    elif isinstance(value, str):
        return colored_value(value) + repr(value)
    elif isinstance(value, (list, dict)):
        try:
            text = json.dumps(value, indent=2, ensure_ascii=False)
            # ایندنت اضافه برای زیبایی در درخت
            text = "\n".join(indent + line for line in text.splitlines())
            return colored_value(value)  + text
        except Exception:
            return colored_value(value) + str(value)  # type: ignore
    else:
        return colored_value(value) + f"<{type(value).__name__}>"


def class_log(obj_or_class: Any) -> None:
    cls = obj_or_class if inspect.isclass(obj_or_class) else obj_or_class.__class__

    print(Fore.CYAN + f"Class: {cls.__name__}")
    print(Fore.YELLOW + "├── Attributes:")

    obj: Any = obj_or_class if not inspect.isclass(obj_or_class) else cls.__new__(cls)  # type: ignore

    attrs = [
        a
        for a in dir(obj)
        if not callable(getattr(obj, a, None)) and not a.startswith("__")
    ]

    if attrs:
        for a in attrs:
            value = getattr(obj, a, None)
            if value is not None:
                val_str = format_value(value)
                print(Fore.GREEN + f"│   ├── {a}: " + val_str)
            else:
                print(Fore.GREEN + f"│   ├── {a}: " + Fore.BLACK + "None")
    else:
        print(Fore.RED + "│   ├── (No attributes)")

    print(Fore.YELLOW + "├── Methods:")

    methods = [
        m for m in dir(cls) if callable(getattr(cls, m)) and not m.startswith("__")
    ]

    if methods:
        for m in methods:
            func = getattr(cls, m)
            sig = inspect.signature(func)
            print(Fore.MAGENTA + f"│   ├── {m}{sig}")
    else:
        print(Fore.RED + "│   ├── (No methods)")


def devlog(data: Any):
    """
    یک تابع کمکی برای چاپ داده‌ها با رنگ‌بندی و فرمت مناسب در کنسول.
    """
    if isinstance(data, (str, int, float, bool, type(None))):
        print(colored_value(data) + repr(data))
    elif isinstance(data, list):
        pprint(
            (data),
        )
    elif isinstance(data, dict):
        pprint(data)
    elif inspect.isclass(data) or hasattr(data, "__class__"):
        pprint(class_log(data))
    else:
        try:
            j = json.dumps(data, indent=4, ensure_ascii=False)
            print(colored_value(j) + j + Style.RESET_ALL)
        except Exception:
            print(Fore.RED + f"<Unprintable {type(data).__name__}>")
