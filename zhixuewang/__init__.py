__author__ = "anwenhu"
__date__ = "2019/8/12 22:30"
__version__ = "1.0.0"

from .zxw import Zhixuewang, get_user_info_by_user_name
VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    "Student", "Teacher", "Zhixuewang", "get_user_info_by_user_name"
]
