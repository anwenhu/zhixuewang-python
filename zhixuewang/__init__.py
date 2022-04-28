__author__ = "anwenhu"
__date__ = "2022/4/27 16:00"
__version__ = "1.1.1"

from zhixuewang.zxw import (login, login_id, rewrite_str, login_student, login_teacher,
                            login_student_id, login_teacher_id, get_session, get_session_id)
from zhixuewang.account import get_session_tgt
from zhixuewang.tools.account import load_account
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
    "get_session_tgt"
]
