from dataclasses import dataclass
from enum import Enum
from typing import List
from zhixuewang.models import (
    Exam,
    Person,
    StuClass,
    Sex,
)


class TeacherRole(Enum):
    TEACHER = "老师"
    HEADMASTER = "校长"
    HEADTEACHER = "班主任"
    SCHOOL_ADMINISTRATOR = "校管理员"
    GRADE_DIRECTER = "年级组长"
    SUBJECT_LEADER = "备课组长"

    def __str__(self):
        return self._value_


class TeaPerson(Person):
    def __init__(
        self,
        name: str = "",
        id: str = "",
        gender: Sex = Sex.GIRL,
        mobile: str = "",
        avatar: str = "",
        code: str = "",
        clazz: StuClass = None,
    ):
        super().__init__(name, id, gender, mobile, avatar)
        self.code = code
        self.clazz = clazz


@dataclass
class MarkingProgress:
    topic_number: str
    complete_rate: float
    complete_count: int
    all_count: int


@dataclass
class PageExam:
    exams: List[Exam]
    page_index: int
    page_size: int
    all_pages: int
    has_next_page: bool


@dataclass
class AcademicInfo:
    term_id: str
    circles_year: str
    teaching_cycle_id: str
    begin_time: int
    end_time: int
    school_id: str
