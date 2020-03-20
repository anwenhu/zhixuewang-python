from enum import Enum
from typing import List, Callable, TypeVar
import datetime


T = TypeVar("T")


class ExtendedList(list, List[T]):
    """扩展列表, 方便找到列表里的元素"""
    def __init__(self, l: list = None):
        super().__init__(l or list())

    def find(self, f: Callable[[object], bool]):
        """返回列表里满足函数f的第一个元素"""
        result = (each for each in self if f(each))
        try:
            return next(result)
        except StopIteration:
            return None

    def find_all(self, f: Callable[[object], bool]):
        """返回列表里所有满足函数f的元素"""
        result = (each for each in self if f(each))
        return ExtendedList(result)

    def find_by_name(self, name: str):
        """返回列表里第一个特定名字的元素"""
        return self.find(lambda d: d.name == name)

    def find_all_by_name(self, name: str):
        """返回列表里所有特定名字的元素"""
        return self.find_all(lambda d: d.name == name)

    def find_by_id(self, id: str):
        """返回列表里第一个特定id的元素"""
        return self.find(lambda d: d.id == id)

    def find_all_by_id(self, id: str):
        """返回列表里所有特定id的元素"""
        return self.find_all(lambda d: d.id == id)


class Phase:
    """学期, 比如七年级, 八年级"""
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code

    def __repr__(self):
        return f"Phase(name={self.name}, code={self.code})"

    def __str__(self):
        return self.__repr__()


class Grade:
    """年级"""
    def __init__(self, name: str, code: str, phase: Phase):
        self.name = name
        self.code = code
        self.phase = phase

    def __repr__(self):
        return f"Grade(name={self.name}, code={self.code}, phase={self.phase})"

    def __str__(self):
        return self.__repr__()


class School:
    """学校"""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id

    def __repr__(self):
        return f"School(id={self.id}, name={self.name})"

    def __str__(self):
        return self.__repr__()


class Sex(Enum):
    """性别"""
    GIRL = "女"
    BOY = "男"


class Person:
    """一些基本属性"""
    def __init__(self,
                 name: str,
                 id: str,
                 gender: Sex = Sex.GIRL,
                 email: str = "",
                 mobile: str = "",
                 qq_number: str = "",
                 birthday: int = 0,
                 avatar: str = ""):
        self.name = name
        self.id = id
        self.gender = gender

        self.email = email
        self.mobile = mobile
        self.qq_number = qq_number

        self.birthday = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=birthday)

        self.avatar = avatar

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, gender={self.gender})"

    def __str__(self):
        return self.__repr__()


class StuClass:
    """班级"""
    def __init__(self, id: str, name: str, grade: Grade, school: School):
        self.id = id
        self.name = name
        self.grade = grade
        self.school = school

    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id

    def __repr__(self):
        return f"StuClass(id={self.id}, name={self.name}, grade={self.grade}, school={self.school})"

    def __str__(self):
        return self.__repr__()


class Exam:
    """考试"""
    def __init__(self,
                 id: str = "",
                 name: str = "",
                 create_user: Person = None,
                 create_time: int = 0,
                 exam_time: int = 0,
                 complete_time: int = 0,
                 status: str = "",
                 grade_code: str = "",
                 subject_codes: List[str] = None,
                 schools: List[School] = None,
                 create_school: School = None):
        self.id = id
        self.name = name
        self.create_user = create_user
        self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=create_time)
        self.exam_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=exam_time)
        self.complete_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=complete_time)
        self.status = status
        self.grade_code = grade_code
        self.subject_codes = subject_codes
        self.schools = schools
        self.create_school = create_school or School("", "")

    def __repr__(self):
        return f"Exam(id={self.id}, name={self.name})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id


class Subject:
    """学科"""
    def __init__(self,
                 id: str,
                 name: str,
                 code: str,
                 status: str = "",
                 create_user: Person = None,
                 create_time: int = 0,
                 standard_score: float = 0,
                 exam: Exam = None):
        self.id = id
        self.name = name
        self.code = code
        self.status = status
        self.create_user = create_user
        self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=create_time)
        self.standard_score = standard_score
        self.exam = exam or Exam()

    def __repr__(self):
        return f"Subject(id={self.id}, name={self.name}, code={self.code}, exam={self.exam})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id


class ExtraRank:
    """关于分数的额外信息"""
    def __init__(self,
                 avg_score: float = 0,
                 high_score: float = 0,
                 rank: int = 0,
                 low_score: float = 0):
        self.avg_score = avg_score
        self.high_score = high_score
        self.rank = rank
        self.low_score = low_score

    def __bool__(self):
        return bool(self.avg_score or self.high_score or self.rank
                    or self.low_score)

    def __repr__(self):
        return f"ExtraRank(avg_score={self.avg_score}, high_score={self.high_score}, rank={self.rank}, low_score={self.low_score})"

    def __str__(self):
        msg = ""
        if not self:
            return msg
        if self.avg_score:
            msg += f"平均分: {self.avg_score}\n"
        if self.high_score:
            msg += f"最高分: {self.high_score}\n"
        if self.low_score:
            msg += f"最低分: {self.low_score}\n"
        if self.rank:
            msg += f"排名: {self.rank}\n"
        return msg[:-1]


class SubjectScore:
    """一门学科的成绩"""
    def __init__(self,
                 score: float,
                 class_rank: ExtraRank = None,
                 grade_rank: ExtraRank = None,
                 subject: Subject = None,
                 person: Person = None,
                 create_time: int = 0):
        self.score = score
        self.class_rank = class_rank or ExtraRank()
        self.grade_rank = grade_rank or ExtraRank()
        self.subject = subject
        self.person = person
        self.create_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=create_time)

    def __repr__(self):
        return f"SubjectScore(score={self.score}, class_rank={self.class_rank}, grade_rank={self.grade_rank}, subject={self.subject}, person={self.person})"

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
