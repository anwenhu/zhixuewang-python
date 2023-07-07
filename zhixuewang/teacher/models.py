from dataclasses import dataclass
from enum import Enum
from zhixuewang.models import (
    Person,
    School,
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
