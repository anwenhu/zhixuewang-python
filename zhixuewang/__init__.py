__author__ = "anwenhu"
__date__ = "2020/2/29 00:40"
__version__ = "1.0.1"

from zhixuewang.zxw import Zhixuewang, get_user_info_by_username, rewrite_str, get_student, get_student_id, get_teacher, get_teacher_id
VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    "Student", "Teacher", "Zhixuewang", "get_user_info_by_username", "rewrite_str", "get_student", "get_student_id", "get_teacher", "get_teacher_id"
]