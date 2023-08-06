from dataclasses import dataclass
from enum import Enum
from typing import List
from zhixuewang.models import (
    Exam,
    Person,
    # School,
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

@dataclass
class QuestionSection:
    code: str
    name: str
    categoryCode: str
    categoryName: str
    sort: int
    isSubjective: bool
    '''是否为客观题'''
    score: int

@dataclass 
class QuestionDifficulty:
    code: str
    name: str
    value: int

@dataclass
class QuestionKnowledges:
    code: str
    name: str
    weight: float
    '''权重'''

@dataclass
class Question:
    id: str
    number: str
    section: QuestionSection
    materials: list
    difficulty: QuestionDifficulty
    knowledges: List[QuestionKnowledges]
    commonKnowledges: List[QuestionKnowledges]
    usedPapers: List[str]
    contentHtml: str
    '''手动解析originalStruct.contentHtml'''
    score: float
    paperName: str
    '''何处来的题目'''
    answerImg: str
    analysisImg: str
    createTime: str
    '''题目创建时间'''
    isXGKQuestion: bool
    '''是否为新高考'''

@dataclass
class Knowledge:
    id: str
    name: str
    isChild: bool
    '''是否为子知识'''
    parentKnowledgeId: str
    '''如果是，上一级的知识ID'''