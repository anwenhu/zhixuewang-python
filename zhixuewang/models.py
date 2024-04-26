import base64
from enum import Enum
import os
import pickle
from typing import List, Callable, Union, TypeVar
from datetime import datetime
from dataclasses import dataclass, field
from zhixuewang.session import get_basic_session, get_session
from zhixuewang.tools.datetime_tool import get_property
from zhixuewang.urls import Url


class Role(Enum):
    student = (0,)
    teacher = 1


@dataclass
class AccountData:
    username: str
    encoded_password: str
    role: Role


class Account:
    def __init__(self, session, role: Role) -> None:
        self._session = session
        self.role = role
        self.username = base64.b64decode(session.cookies["uname"].encode()).decode()

    def save_account(self, path: str = "user.data"):
        with open(path, "wb") as f:
            password = base64.b64decode(self._session.cookies["pwd"].encode()).decode()
            data = pickle.dumps(
                AccountData(
                    self.username, password, self.role
                )
            )
            f.write(base64.b64encode(data))

    def update_login_status(self):
        """更新登录状态. 如果session过期自动重新获取"""
        r = self._session.get(Url.GET_LOGIN_STATE)
        data = r.json()
        if data["result"] == "success":
            return
        # session过期
        password = base64.b64decode(self._session.cookies["pwd"].encode()).decode()
        self._session = get_session(self.username, password)


T = TypeVar("T")


class ExtendedList(List[T]):
    """扩展列表, 方便找到列表里的元素"""

    def __init__(self, ls: List[T] = None):
        super().__init__(list() if ls is None else ls)

    def foreach(self, f: Callable[[T], None]):
        for each in self:
            f(each)

    def find(self, f: Callable[[T], bool]) -> Union[T, None]:
        """返回列表里满足函数f的第一个元素"""
        result = (each for each in self if f(each))
        try:
            return next(result)
        except StopIteration:
            return None

    def find_all(self, f: Callable[[T], bool]) -> "ExtendedList[T]":
        """返回列表里所有满足函数f的元素"""
        result = (each for each in self if f(each))
        return ExtendedList(list(result))

    def find_by_name(self, name: str) -> Union[T, None]:
        """返回列表里第一个特定名字的元素, 没有则返回None"""
        return self.find(lambda d: d.name == name)

    def find_all_by_name(self, name: str) -> "ExtendedList[T]":
        """返回列表里所有特定名字的元素"""
        return self.find_all(lambda d: d.name == name)

    def find_by_id(self, spec_id: str) -> Union[T, None]:
        """返回列表里第一个特定id的元素, 没有则返回None"""
        return self.find(lambda d: d.id == spec_id)

    def find_all_by_id(self, spec_id: str) -> "ExtendedList[T]":
        """返回列表里所有特定id的元素"""
        return self.find_all(lambda d: d.id == spec_id)


@dataclass
class Grade:
    """年级"""

    name: str = ""
    code: str = ""
    phase_name: str = ""
    phase_code: str = ""


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


@dataclass(repr=False)
class Person:
    """一些基本属性"""

    id: str = ""
    name: str = ""
    gender: Sex = Sex.GIRL
    mobile: str = ""
    avatar: str = ""


@dataclass(repr=False)
class StuPerson(Person):
    """一些关于学生的信息"""

    code: str = ""
    clazz: StuClass = field(default_factory=StuClass, repr=False)

    def __str__(self):
        return (
            f"{self.clazz} 姓名: {self.name} 性别: {self.gender} "
            f"{f'手机号码: {self.mobile}' if self.mobile != '' else ''}"
        )


@dataclass
class BasicSubject:
    """学科基本信息"""

    name: str = ""
    code: str = ""


@dataclass(eq=False)
class Subject(BasicSubject):
    """学科"""

    id: str = ""
    standard_score: float = 0
    status: str = field(default="", repr=False)
    exam_id: str = field(default="", repr=False)
    create_user: Person = field(default_factory=Person, repr=False)
    create_time: float = field(default=0, repr=False)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass
class TextBook:
    """教科书属性"""
    code: str = ""
    """教科书编号"""
    name: str = ""
    """教科书名称"""
    version: str = ""
    """教科书版本，如北师大、人教、部编等"""
    versionCode: int = 0
    """教科书版本编号"""
    bindSubject: BasicSubject = field(default_factory=BasicSubject)
    def __str__(self) -> str:
        return f"{self.bindSubject.name} {self.name} ({self.version})"
        

@dataclass(eq=False)
class Exam:
    """考试"""

    id: str = ""
    name: str = ""
    status: str = ""
    grade_code: str = ""
    subjects: ExtendedList[Subject] = field(default_factory=ExtendedList, repr=False)
    schools: ExtendedList[School] = field(default_factory=ExtendedList, repr=False)
    create_user: Person = field(default_factory=Person, repr=False)
    create_time: float = field(default=0, repr=False)
    class_rank: int = field(default=0, repr=False)
    grade_rank: int = field(default=0, repr=False)
    is_final: bool = False

    def __bool__(self):
        return bool(self.id)

    def __eq__(self, other):
        return type(other) == type(self) and other.id == self.id


@dataclass
class SubjectScore:
    """一门学科的成绩"""

    score: float = 0
    subject: Subject = field(default_factory=Subject)
    person: StuPerson = field(default_factory=StuPerson)
    class_rank: int = field(default_factory=int, compare=False)
    grade_rank: int = field(default_factory=int, compare=False)
    exam_rank: int = field(default_factory=int, compare=False)

    def __str__(self) -> str:
        if self.person.id == "":  # mark
            data = f"{self.subject.name}: {self.score}"
            if self.class_rank != 0:
                data += f" (班级第{self.class_rank}名)"
            return data
        return self.__repr__()


class Mark(ExtendedList[SubjectScore]):
    """一场考试的成绩"""

    def __init__(
            self, ls: list = None, exam: Exam = Exam(), person: StuPerson = StuPerson()
    ):

        super().__init__([] if ls is None else ls)
        self.exam = exam
        self.person = person

    def __repr__(self):
        if self.exam and self.person:
            msg = f"{self.person.name}-{self.exam.name}\n" + "".join(
                [f"{subject}\n" for subject in self]
            )
            return msg[:-1]

    def __str__(self):
        return self.__repr__()


@dataclass
class MarkingRecord:
    """批改记录"""

    time: datetime
    score: float
    teacher_name: str


@dataclass
class SubTopicRecord:
    """小题得分详情"""

    score: float
    marking_records: Union[None, ExtendedList[MarkingRecord]]


@dataclass
class TopicRecord:
    """题目得分详情"""

    title: str
    score: float
    standard_score: float
    subtopic_records: Union[None, ExtendedList[SubTopicRecord]]


class AnswerRecord(ExtendedList[TopicRecord]):
    """一场考试的得分详情"""


@dataclass
class HwType:
    """作业类型, eg: 105 自由出题"""

    name: str
    code: int


@dataclass
class Homework:
    id: str
    title: str = ""
    type: HwType = field(default_factory=HwType)
    begin_time: int = 0
    end_time: int = 0
    create_time: int = 0
    subject_name: str = ""
    is_allow_makeup: bool = False  # 是否允许重做
    class_id: str = ""


@dataclass
class StuHomework(Homework):
    stu_hwid: str = ""


@dataclass
class HwResource:
    path: str
    name: str

    def download(self, path: str):
        r = get_basic_session().get(self.path)
        with open(os.path.join(path, self.name), "wb") as f:
            f.write(r.content)


@dataclass
class HwAnswer:
    title: str = ""
    content: str = ""


@dataclass
class ErrorBookTopic:
    analysis_html: str
    answer_html: str
    answer_type: str
    is_correct: bool
    class_score_rate: float
    content_html: str
    difficulty: int
    dis_title_number: str
    paper_id: str
    subject_name: str
    score: float
    standard_answer: str  # 网址
    standard_score: float
    topic_set_id: str
    topic_img_url: str  # 好看的题目
    topic_source_paper_name: str
    image_answer: List[str]  # 你的答案
    topic_analysis_img_url: str
