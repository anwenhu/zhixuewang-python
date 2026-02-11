__author__ = "anwenhu,MasterYuan418,immoses648,krn1pnc,Haorwen,amakerlife"
__date__ = "2025/11/17 21:58"
__version__ = "1.4.0"

from zhixuewang.account import (
    login_cookie,
    login_playwright,
    rewrite_str,
)

VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    "login_cookie",
    "login_playwright",
    "rewrite_str",
]
