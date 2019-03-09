__author__ = 'anwenhu'
__date__ = '2019/2/7 16:10'
__version__ = "0.1.7"

from .zxw import Zhixuewang

VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    'person.py', 'Zhixuewang', 'exam', 'exceptions'
]
