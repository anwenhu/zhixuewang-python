from enum import Enum
from typing import List, Callable, TypeVar
from dataclasses import dataclass, field
import datetime


T = TypeVar("T")


class ExtendedList(list, List[T]):
    """扩展列表, 方便找到列表里的元素"""
    def __init__(self, l: List[T] = None):
        super().__init__(l or list())

    def find(self, f: Callable[[T], bool]):
        """返回列表里满足函数f的第一个元素"""
        result = (each for each in self if f(each))
        try:
            return next(result)
        except StopIteration:
            return None

    def find_all(self, f: Callable[[T], bool]) -> List[T]:
        """返回列表里所有满足函数f的元素"""
        result = (each for each in self if f(each))
        return ExtendedList(result)

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
    name: str
    code: str


@dataclass
class Grade:
    """年级"""
    name: str
    code: str
    phase: Phase


@dataclass
class School:
    """学校"""
    id: str = ""
    name: str = ""


class Sex(Enum):
    """性别"""
    GIRL = "女"
    BOY = "男"


@dataclass
class Person:
    """一些基本属性"""
    id: str = ""
    name: str = ""
    gender: Sex = Sex.GIRL
    email: str = ""
    mobile: str = ""
    qq_number: str = ""
    birthday: datetime.datetime = datetime.datetime(1970, 1, 1)
    avatar: str = ""

    def __post_init__(self):
        if isinstance(self.birthday, int):
            self.birthday = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.birthday)


@dataclass
class StuClass:
    """班级"""
    id: str
    name: str
    grade: Grade
    school: School


@dataclass(eq=False)
class Exam:
    """考试"""
    id: str = ""
    name: str = ""
    status: str = ""
    grade_code: str = ""
    subject_codes: List[str] = None
    schools: List[School] = None
    create_school: School = School()
    create_user: Person = Person()
    create_time: datetime.datetime = datetime.datetime(1970, 1, 1)
    exam_time: datetime.datetime = datetime.datetime(1970, 1, 1)
    complete_time: datetime.datetime = datetime.datetime(1970, 1, 1)

    def __post_init__(self):
        if isinstance(self.create_time, int):
            self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.create_time)
        if isinstance(self.exam_time, int):
            self.exam_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.exam_time)
        if isinstance(self.complete_time, int):
            self.complete_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.complete_time)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass(eq=False)
class Subject:
    """学科"""
    id: str = ""
    name: str = ""
    code: str = ""
    standard_score: float = 0
    status: str = ""
    exam: Exam = Exam()
    create_user: Person = Person()
    create_time: datetime.datetime = datetime.datetime(1970, 1, 1)

    def __post_init__(self):
        if isinstance(self.create_time, int):
            self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.create_time)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass
class ExtraRank:
    """关于分数的额外信息"""
    rank: int = 0
    avg_score: float = 0
    low_score: float = 0
    high_score: float = 0

    def __str__(self):
        msg = ""
        if not (self.rank or self.avg_score or self.low_score or self.high_score):
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
    score: float
    subject: Subject
    person: Person
    create_time: datetime.datetime = datetime.datetime(1970, 1, 1)
    class_rank: ExtraRank = field(default=ExtraRank(), compare=False)
    grade_rank: ExtraRank = field(default=ExtraRank(), compare=False)

    def __post_init__(self):
        if isinstance(self.create_time, int):
            self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.create_time)

    def __str__(self):
        msg = f"{self.person.name} {self.subject.name}:\n分数: {self.score}\n"
        if self.class_rank:
            msg += f"班级:\n{self.class_rank}\n"
        if self.grade_rank:
            msg += f"年级:\n{self.grade_rank}\n"
        return msg[:-1]


class Mark(ExtendedList):
    """一场考试的成绩"""
    def __init__(self, l: list = None, exam: Exam = None):
        super().__init__(l)
        self.exam = exam

    def __repr__(self):
        msg = "".join([f"{subject}\n" for subject in self])
        return msg[:-1]

    def __str__(self):
        return self.__repr__()


class subjectTable(Enum):
    chinese = ""
    math = ""
    english = ""
    physics = "01"
    chemisry = ""
    history = ""
