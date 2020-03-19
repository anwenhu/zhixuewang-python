from typing import List
from zhixuewang.models import Person, ExtendedList, StuClass, Sex, School


class StuPerson(Person):
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
                 clazz: StuClass = None):
        super().__init__(name, id, gender, email, mobile, qq_number, birthday,
                         avatar)
        self.code = code
        self.clazz = clazz


class StuPersonList(ExtendedList):
    def find_by_code(self, code: str) -> StuPerson:
        return self.find(lambda p: p.code == code)

    def find_all_by_code(self, code: str) -> List[StuPerson]:
        return self.find_all(lambda p: p.code == code)

    def find_by_clazz_id(self, clazz_id: str) -> StuPerson:
        return self.find(lambda p: p.clazz.id == clazz_id)

    def find_all_by_clazz_id(self, clazz_id: str) -> List[StuPerson]:
        return self.find_all(lambda p: p.clazz.id == clazz_id)

    def find_by_clazz(self, clazz: StuClass) -> StuPerson:
        return self.find(lambda p: p.clazz == clazz)

    def find_all_by_clazz(self, clazz: StuClass) -> List[StuPerson]:
        return self.find_all(lambda p: p.clazz == clazz)

    def find_by_school_id(self, school_id: str) -> StuPerson:
        return self.find(lambda p: p.school.id == school_id)

    def find_all_by_school_id(self, school_id: str) -> List[StuPerson]:
        return self.find_all(lambda p: p.school.id == school_id)

    def find_by_school(self, school: School) -> StuPerson:
        return self.find(lambda p: p.school == school)

    def find_all_by_school(self, school: School) -> List[StuPerson]:
        return self.find_all(lambda p: p.school == school)
