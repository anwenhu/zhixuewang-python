__author__ = "anwenhu"
__date__ = "2019/3/15 22:30"
__version__ = "0.1.8"

from .zxw import Zhixuewang
VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    "person", "Zhixuewang", "exam", "exceptions", "models", "zxw"
]
