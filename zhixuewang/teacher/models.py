from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from zhixuewang.models import (
    BasicSubject,
    Exam,
    Grade,
    Person,
)

ROLE_TABLE = {
    "teacher": "老师",
    "subjectLeader": "备课组长",
    "gradeDirecter": "年级组长",
    "headteacher": "班主任",
    "headmaster": "校长",
    "viceHeadteacher": "副班主任",
    "viceHeadmaster": "副校长",
    "schoolAdministrator": "校管理员",
}
class TeacherRole(Enum):
    TEACHER = "老师"
    HEADMASTER = "校长"
    VICE_HEADMASTER = "副校长"
    VICE_HEADTEACHER = "副班主任"
    HEADTEACHER = "班主任"
    SCHOOL_ADMINISTRATOR = "校管理员"
    GRADE_DIRECTER = "年级组长"
    SUBJECT_LEADER = "备课组长"

    def __str__(self):
        return self._value_
    
    @staticmethod
    def from_zxw(label: str) -> "TeacherRole":
        if label in ROLE_TABLE:
            return TeacherRole(ROLE_TABLE[label])
        else:
            raise ValueError(f"未知的教师角色: {label}")
    
    def to_zxw(self) -> str:
        for key, value in ROLE_TABLE.items():
            if value == self.value:
                return key
        raise ValueError(f"无法转换教师角色: {self.value}")


@dataclass
class Phase:
    """学段"""
    code: str = ""
    name: str = ""


@dataclass
class Region:
    """地区"""
    code: str = ""
    name: str = ""
    level: Optional[str] = None
    id: str = ""


@dataclass
class PhaseSubjectGrade:
    """学段-学科-年级信息"""
    phase: Phase = field(default_factory=Phase)
    subjects: List[BasicSubject] = field(default_factory=list)
    grades: List[Grade] = field(default_factory=list)


@dataclass(repr=False)
class TeaPerson(Person):
    """教师基本信息"""
    login_name: str = ""
    """登录名"""
    roles: List[TeacherRole] = field(default_factory=list)
    """教师角色列表"""
    province: Optional[Region] = None
    """省份"""
    city: Optional[Region] = None
    """城市"""
    district: Optional[Region] = None
    """区县"""
    
    def __str__(self):
        return f"教师: {self.name} ({self.login_name})"


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
class TeacherMarkingRecord:
    """教师批改记录"""
    score: float
    """给分"""
    marking_time: int
    """批改时间（毫秒时间戳）"""
    teacher_name: str = ""
    """批改教师姓名"""
    teacher_id: str = ""
    """批改教师ID"""
    role: str = ""
    """批改角色（marking1等）"""
    is_excellent: bool = False
    """是否优秀"""
    is_typical_error: bool = False
    """是否典型错误"""
    marking_content: str = ""
    """批改内容（JSON字符串）"""


@dataclass
class SubTopicDetail:
    """小题详情"""
    score: float
    """得分"""
    sub_topic_index: int = -1
    """小题索引"""
    score_source: str = ""
    """得分来源"""
    teacher_marking_records: List[TeacherMarkingRecord] = field(default_factory=list)
    """教师批改记录"""


@dataclass
class AnswerRecordDetail:
    """答题详情"""
    topic_number: int
    """题号"""
    disp_title: str
    """显示题号"""
    answer: str
    """学生答案（文本）"""
    score: float
    """得分"""
    standard_score: float
    """满分"""
    is_correct: bool
    """是否正确"""
    answer_type: str
    """答题类型（s01Text/s02Image等）"""
    source_category_name: str = ""
    """题型名称（单选题、主观题等）"""
    topic_type_id: str = ""
    """题型ID"""
    sub_topics: List[SubTopicDetail] = field(default_factory=list)
    """小题列表（主观题）"""
    is_excellent: bool = False
    """是否优秀"""
    is_typical_error: bool = False
    """是否典型错误"""
    marking_paper_topic_id: str = ""
    """批改试卷题目ID"""


@dataclass
class OriginalPaper:
    """原卷数据"""
    user_id: str
    """学生ID"""
    topic_set_id: str
    """科目ID"""
    total_score: float
    """总分"""
    answer_details: List[AnswerRecordDetail] = field(default_factory=list)
    """答题详情列表"""
    answer_sheet_images: List[str] = field(default_factory=list)
    
    
    @property
    def objective_questions(self) -> List[AnswerRecordDetail]:
        """获取客观题列表"""
        return [detail for detail in self.answer_details if detail.answer_type == "s01Text"]
    
    @property
    def subjective_questions(self) -> List[AnswerRecordDetail]:
        """获取主观题列表"""
        return [detail for detail in self.answer_details if detail.answer_type == "s02Image"]
    
    @property
    def total_objective_score(self) -> float:
        """获取客观题总分"""
        return sum(detail.score for detail in self.objective_questions)
    
    @property
    def total_subjective_score(self) -> float:
        """获取主观题总分"""
        return sum(detail.score for detail in self.subjective_questions)
