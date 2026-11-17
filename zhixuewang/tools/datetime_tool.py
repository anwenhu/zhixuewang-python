import datetime
from typing import Optional


def timestamp2datetime(timestamp: float) -> datetime.datetime:
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)


def iso2timestamp(time_str: Optional[str]) -> Optional[int]:
    """将 ISO 8601 时间字符串(如 2026-09-20T09:15:39.000+00:00)转为毫秒时间戳"""
    if not time_str:
        return None
    return int(datetime.datetime.fromisoformat(time_str).timestamp() * 1000)


def cst2timestamp(time_str: Optional[str]) -> Optional[int]:
    """将北京时间字符串(如 2026-09-20 17:15:39)转为毫秒时间戳"""
    if not time_str:
        return None
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8))).timestamp() * 1000)


def get_property(arg_name: str) -> property:
    def setter(self, mill_timestamp):
        self.__dict__[arg_name] = timestamp2datetime(mill_timestamp / 1000)

    return property(fget=lambda self: self.__dict__[arg_name],
                    fset=setter)
