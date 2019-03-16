import time
from collections import namedtuple

class schoolDataModel(namedtuple("schoolDataModel", [
        "schoolId",
        "schoolName"
    ])):
    pass

class classDataModel(namedtuple("classDataModel", [
        "classId",
        "className"
    ])):
    pass

class birthdayModel:
    def __init__(self, t: int):
        self.__t = t
        self.__d = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(t))
    
    def get_timestamp(self):
        return self.__t

    def __str__(self):
        return self.__d
    
    def __repr__(self):
        return self.__d