from enum import Enum
from typing import List, Callable, TypeVar
from dataclasses import dataclass, field
from zhixuewang.tools.datetime_tool import get_property

T = TypeVar("T")


class ExtendedList(List[T]):
    """扩展列表, 方便找到列表里的元素"""

    def __init__(self, l: List[T] = None):
        super().__init__(l or list())

    def foreach(self, f: Callable[[T], None]):
        for each in self:
            f(each)

    def find(self, f: Callable[[T], bool]) -> T:
        """返回列表里满足函数f的第一个元素"""
        result = (each for each in self if f(each))
        try:
            return next(result)
        except StopIteration:
            return None

    def find_all(self, f: Callable[[T], bool]) -> List[T]:
        """返回列表里所有满足函数f的元素"""
        result = (each for each in self if f(each))
        return ExtendedList(list(result))

    def find_by_name(self, name: str) -> T:
        """返回列表里第一个特定名字的元素"""
        return self.find(lambda d: d.name == name)

    def find_all_by_name(self, name: str) -> List[T]:
        """返回列表里所有特定名字的元素"""
        return self.find_all(lambda d: d.name == name)

    def find_by_id(self, id: str) -> T:
        """返回列表里第一个特定id的元素"""
        return self.find(lambda d: d.id == id)

    def find_all_by_id(self, id: str) -> List[T]:
        """返回列表里所有特定id的元素"""
        return self.find_all(lambda d: d.id == id)


@dataclass
class Phase:
    """学期, 比如七年级, 八年级"""
    name: str = ""
    code: str = ""


@dataclass
class Grade:
    """年级"""
    name: str = ""
    code: str = ""
    phase: Phase = field(default_factory=Phase)


@dataclass
class School:
    """学校"""
    id: str = ""
    name: str = ""

    def __str__(self):
        return self.name


class Sex(Enum):
    """性别"""
    GIRL = "女"
    BOY = "男"

    def __str__(self):
        return self._value_


@dataclass(eq=False)
class StuClass:
    """班级"""
    id: str = ""
    name: str = ""
    grade: Grade = field(default_factory=Grade, repr=False)
    school: School = field(default_factory=School, repr=False)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id

    def __str__(self):
        return f"学校: {self.school} 班级: {self.name}"

    def __repr__(self):
        return f"StuClass(id={self.id}, name={self.name}, school={self.school.__repr__()})"


@dataclass(repr=False)
class Person:
    """一些基本属性"""
    id: str = ""
    name: str = ""
    gender: Sex = Sex.GIRL
    email: str = ""
    mobile: str = ""
    qq_number: str = ""
    _birthday_timestamp: float = 0
    birthday = get_property("_birthday_timestamp")
    avatar: str = ""


@dataclass(repr=False)
class StuPerson(Person):
    """一些关于学生的信息"""
    code: str = ""
    clazz: StuClass = field(default_factory=StuClass, repr=False)
    

    def __str__(self):
        return f"{self.clazz} 姓名: {self.name} 性别: {self.gender} " \
               f"{f'QQ: {self.qq_number} ' if self.qq_number != '' else ''}" \
               f"{f'手机号码: {self.mobile}' if self.mobile != '' else ''}"

    def __repr__(self):
        return f"Person(id={self.id}, clazz={self.clazz.__repr__()}, name={self.name}, gender={self.gender}" \
               f"{f', qq_number={self.qq_number}' if self.qq_number != '' else ''}" \
               f"{f', mobile={self.mobile}' if self.mobile != '' else ''}" + ")"




@dataclass(eq=False)
class Exam:
    """考试"""
    id: str = ""
    name: str = ""
    status: str = ""
    grade_code: str = ""
    subject_codes: ExtendedList[str] = field(default_factory=ExtendedList, repr=False)
    schools: ExtendedList[School] = field(default_factory=ExtendedList, repr=False)
    create_school: School = field(default_factory=School, repr=False)
    create_user: Person = field(default_factory=Person, repr=False)
    _create_timestamp: float = field(default=0, repr=False)
    create_time = get_property("_create_timestamp")
    _exam_timestamp: float = field(default=0, repr=False)
    exam_time = get_property("_exam_timestamp")
    _complete_timestamp: float = field(default=0, repr=False)
    complete_time = get_property("_complete_timestamp")
    class_rank: int = field(default=0, repr=False)
    grade_rank: int = field(default=0, repr=False)
    is_final: bool = False

    def __bool__(self):
        return bool(self.id)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass(eq=False)
class Subject:
    """学科"""
    id: str = ""
    name: str = ""
    code: str = ""
    standard_score: float = 0
    status: str = field(default="", repr=False)
    exam: Exam = field(default_factory=Exam, repr=False)
    create_user: Person = field(default_factory=Person, repr=False)
    _create_timestamp: float = field(default=0, repr=False)
    create_time = get_property("_create_timestamp")

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass(eq=False)
class ExamInfo(Exam):
    classId: str = ""
    subjects: ExtendedList[Subject] = field(default_factory=ExtendedList, repr=False)


@dataclass
class ExtraRank:
    """关于分数的额外信息"""
    rank: int = 0
    avg_score: float = 0
    low_score: float = 0
    high_score: float = 0

    def __bool__(self):
        return bool(self.rank or self.avg_score or self.low_score or self.high_score)

    def __str__(self):
        msg = ""
        if not self:
            return msg
        if self.rank:
            msg += f"排名: {self.rank}\n"
        if self.avg_score:
            msg += f"平均分: {self.avg_score}\n"
        if self.low_score:
            msg += f"最低分: {self.low_score}\n"
        if self.high_score:
            msg += f"最高分: {self.high_score}\n"
        return msg[:-1]


@dataclass
class SubjectScore:
    """一门学科的成绩"""
    score: float = 0
    subject: Subject = field(default_factory=Subject)
    person: StuPerson = field(default_factory=StuPerson)
    _create_timestamp: float = field(default=0, repr=False)
    create_time = get_property("_create_timestamp")
    class_extraRank: ExtraRank = field(default_factory=ExtraRank, compare=False)
    grade_extraRank: ExtraRank = field(default_factory=ExtraRank, compare=False)
    exam_extraRank: ExtraRank = field(default_factory=ExtraRank, compare=False)

    def __str__(self):
        msg = f"{self.subject.name}:\n分数: {self.score}\n"
        if self.class_extraRank:
            msg += f"班级:\n{self.class_extraRank}\n"
        if self.grade_extraRank:
            msg += f"年级:\n{self.grade_extraRank}\n"
        if self.exam_extraRank:
            msg += f"联考:\n{self.exam_extraRank}\n"
        return msg[:-1]


class Mark(ExtendedList[SubjectScore]):
    """一场考试的成绩"""

    def __init__(self, l: list = None, exam: Exam = None, person: StuPerson = None):
        super().__init__(l)
        self.exam = exam
        self.person = person

    def __repr__(self):
        if self.exam and self.person:
            msg = f"{self.person.name}-{self.exam.name}\n" + \
                "".join([f"{subject}\n" for subject in self])
            return msg[:-1]

    def __str__(self):
        return self.__repr__()



class StuPersonList(ExtendedList):
    """学生列表"""

    def find_by_code(self, code: str) -> StuPerson:
        """返回第一个准考证号为code的学生"""
        return self.find(lambda p: p.code == code)

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

    def find_by_school(self, school: School) -> StuPerson:
        """返回第一个学校为school的学生"""
        return self.find(lambda p: p.school == school)



class SubjectTable(Enum):
    chinese = ""
    math = ""
    english = ""
    physics = "01"
    chemisry = ""
    history = ""
