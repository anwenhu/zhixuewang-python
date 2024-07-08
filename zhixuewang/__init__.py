__author__ = "anwenhu,MasterYuan418,immoses648,krn1pnc,Haorwen"
__date__ = "2024/6/25 14:00"
__version__ = "1.3.1"

from zhixuewang.account import (login, login_id, rewrite_str, login_student, login_teacher,
                                login_student_id, login_teacher_id, load_account)
from zhixuewang.session import get_session, get_session_id

VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    "login",
    "login_id",
    "rewrite_str",
    "login_student",
    "login_teacher",
    "login_student_id",
    "login_teacher_id",
    "get_session",
    "get_session_id",
    "load_account",
]
