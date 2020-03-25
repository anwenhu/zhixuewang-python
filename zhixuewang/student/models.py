from dataclasses import dataclass
from zhixuewang.models import Person, ExtendedList, StuClass, Sex, School


@dataclass
class StuPerson(Person):
    """一些关于学生的信息"""
    name: str = ""
    id: str = ""
    gender: Sex = Sex.GIRL
    email: str = ""
    mobile: str = ""
    qq_number: str = ""
    birthday: int = 0
    avatar: str = ""
    code: str = ""
    clazz: StuClass = None


class StuPersonList(ExtendedList):
    """学生列表"""
    def find_by_code(self, code: str) -> StuPerson:
        """返回第一个准考证号为code的学生"""
        return self.find(lambda p: p.code == code)

    def find_all_by_code(self, code: str) -> ExtendedList[StuPerson]:
        """返回所有准考证号为code的学生(其实不存在)"""
        return self.find_all(lambda p: p.code == code)

    def find_by_clazz_id(self, clazz_id: str) -> StuPerson:
        """返回第一个班级id为clazz_id的学生"""
        return self.find(lambda p: p.clazz.id == clazz_id)

    def find_all_by_clazz_id(self, clazz_id: str) -> ExtendedList[StuPerson]:
        """返回所有班级id为clazz_id的学生"""
        return self.find_all(lambda p: p.clazz.id == clazz_id)

    def find_by_clazz(self, clazz: StuClass) -> StuPerson:
        """返回第一个班级为clazz的学生"""
        return self.find(lambda p: p.clazz == clazz)

    def find_all_by_clazz(self, clazz: StuClass) -> ExtendedList[StuPerson]:
        """返回所有班级为clazz的学生"""
        return self.find_all(lambda p: p.clazz == clazz)

    def find_by_school_id(self, school_id: str) -> StuPerson:
        """返回第一个学校id为school_id的学生"""
        return self.find(lambda p: p.school.id == school_id)

    def find_all_by_school_id(self, school_id: str) -> ExtendedList[StuPerson]:
        """返回所有学校id为school_id的学生(其实不存在)"""
        return self.find_all(lambda p: p.school.id == school_id)

    def find_by_school(self, school: School) -> StuPerson:
        """返回第一个学校为school的学生"""
        return self.find(lambda p: p.school == school)

    def find_all_by_school(self, school: School) -> ExtendedList[StuPerson]:
        """返回所有学校为school的学生(其实不存在)"""
        return self.find_all(lambda p: p.school == school)
