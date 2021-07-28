from enum import Enum
from typing import List
from zhixuewang.models import Person, StuClass, Sex


class TeacherRole(Enum):
    TEACHER = "老师"
    HEADMASTER = "校长"

    def __str__(self):
        return self._value_


class TeaPerson(Person):
    def __init__(self,
                 name: str = "",
                 id: str = "",
                 gender: Sex = Sex.GIRL,
                 email: str = "",
                 mobile: str = "",
                 qq_number: str = "",
                 birthday: int = 0,
                 avatar: str = "",
                 code: str = "",
                 clazz: StuClass = None,
                 roles: List[TeacherRole] = [TeacherRole.TEACHER]):
        super().__init__(name, id, gender, email, mobile, qq_number, birthday,
                         avatar)
        self.code = code
        self.clazz = clazz


# class TeaPersonList(ExtendedList):
#     def find_by_code(self, code: str) -> StuPerson:
#         return self.find(lambda p: p.code == code)

#     def find_by_clazz_id(self, clazz_id: str) -> StuPerson:
#         return self.find(lambda p: p.clazz.id == clazz_id)

#     def find_by_clazz(self, clazz: StuClass) -> StuPerson:
#         return self.find(lambda p: p.clazz == clazz)

#     def find_by_school_id(self, school_id: str) -> StuPerson:
#         return self.find(lambda p: p.school.id == school_id)

#     def find_by_school(self, school: School) -> StuPerson:
#         return self.find(lambda p: p.school == school)
