__author__ = "anwenhu"
__date__ = "2020/8/6 10:27"
__version__ = "1.0.4"

from zhixuewang.zxw import (login, login_id, rewrite_str, login_student, login_teacher,
                            login_student_id, login_teacher_id, get_session, get_session_id)
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
]
