__author__ = "anwenhu,MasterYuan418,immoses648,krn1pnc,Haorwen,amakerlife"
__date__ = "2025/5/2 11:05"
__version__ = "1.3.4"

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
    "load_account",
]
