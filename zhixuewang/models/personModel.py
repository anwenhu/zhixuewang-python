from .basicModel import listModel
import time
from typing import List


class schoolModel:
    def __init__(self, id: str = "", name: str = ""):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"school(name={self.name}, id={self.id})"

    def __eq__(self, school):
        return self.id == school.id


class classModel:
    def __init__(self, id: str = "", name: str = ""):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"class(name={self.name}, id={self.id})"

    def __eq__(self, clazz):
        return self.id == clazz.id


class birthdayModel:
    def __init__(self, t: int):
        self.t = t
        self.d = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(t))

    def get_timestamp(self):
        return self.t

    def __str__(self):
        return self.d

    def __repr__(self):
        return self.d


class personModel:
    def __init__(self,
                 name: str = "",
                 id: str = "",
                 code: str = "",
                 birthday: int = 0,
                 qq_number: str = "",
                 avatar: str = "",
                 gender: str = "",
                 email: str = "",
                 mobile: str = "",
                 clazz: classModel = classModel(),
                 teaching_clazzs: List[classModel] = list(),
                 school: schoolModel = schoolModel()):
        self.avatar = avatar
        self.name = name
        self.id = id
        self.code = code
        self.gender = gender
        self.birthday = birthdayModel(birthday)
        self.qq_number = qq_number
        self.email = email
        self.mobile = mobile
        self.clazz = clazz
        self.teaching_clazzs = teaching_clazzs
        self.school = school

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"person(name={self.name}, id={self.id}, code={self.code})"


class personsModel(listModel):
    def findByCode(self, code: str) -> personModel:
        return self.find(lambda p: p.code == code)

    def findByClazz(self, clazz: classModel) -> personModel:
        return self.find(lambda p: p.clazz == clazz)

    def findBySchool(self, school: schoolModel) -> personModel:
        return self.find(lambda p: p.school == school)
