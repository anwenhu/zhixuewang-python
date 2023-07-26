__author__ = "anwenhu"
__date__ = "2023/7/26 12:30"
__version__ = "1.1.9"

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
