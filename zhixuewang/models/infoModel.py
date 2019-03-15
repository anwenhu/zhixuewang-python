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
