import base64
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional, TypeVar

from requests import Session

from zhixuewang.session import get_basic_session
from zhixuewang.urls import Url

if TYPE_CHECKING:
    from zhixuewang.parent.parent import ParentAccount
    from zhixuewang.student.student import StudentAccount
    from zhixuewang.teacher.teacher import TeacherAccount


class Role(Enum):
    student = 0
    teacher = 1
    parent = 2


class Account:
    def __init__(self, session: Session, role: Role) -> None:
        self._session = session
        self.role = role
        self.username = base64.b64decode(session.cookies["uname"].encode()).decode()

    def get_session(self):
        return self._session
    
    def to_student(self) -> "StudentAccount":
        raise NotImplementedError("账号无法转换为学生账号")
    
    def to_teacher(self) -> "TeacherAccount":
        raise NotImplementedError("账号无法转换为教师账号")
    
    def to_parent(self) -> "ParentAccount":
        raise NotImplementedError("账号无法转换为家长账号")
    
    def get_personal_messages(
        self, 
        page_index: int = 1, 
        page_size: int = 10000
    ) -> "PersonalMessageList":
        """获取私信消息列表
        Args:
            page_index (int): 页码，从1开始
            page_size (int): 每页大小
        Returns:
            PersonalMessageList: 私信消息列表对象
        """
        import time
        timestamp = int(time.time() * 1000)
        r = self._session.get(
            Url.GET_PERSONAL_MESSAGES,
            params={
                "_t": timestamp,
                "pageIndex": page_index,
                "pageSize": page_size,
                "type": "personalMsg",
                "_": timestamp - 300
            }
        )
        data = r.json()
        
        # 解析消息列表
        messages = []
        pager_messages = data.get("pagerMessages", {})
        for msg_data in pager_messages.get("list", []):
            notify = msg_data.get("notify", {})
            
            # 解析发送者信息
            sender_detail_str = notify.get("senderDetail", "{}")
            try:
                sender_detail = json.loads(sender_detail_str) if isinstance(sender_detail_str, str) else sender_detail_str
            except json.JSONDecodeError:
                sender_detail = {}
            
            sender = MessageUser(
                user_id=sender_detail.get("userId", ""),
                user_name=sender_detail.get("userName", ""),
                role=sender_detail.get("role", ""),
                school_id=sender_detail.get("schoolId", ""),
                area_id=sender_detail.get("areaId", ""),
                city_id=sender_detail.get("cityId", ""),
                country_id=sender_detail.get("countryId", ""),
                province_id=sender_detail.get("provinceId", "")
            )
            
            messages.append(PersonalMessage(
                id=notify.get("id", 0),
                content=notify.get("content", ""),
                create_time=notify.get("createTime", 0),
                update_time=notify.get("updateTime", 0),
                send_user_id=notify.get("sendUserId", ""),
                sender=sender,
                notify_id=msg_data.get("notifyId", 0),
                subscriber=msg_data.get("subscriber", ""),
                subscriber_name=msg_data.get("subscriberName", ""),
                subscriber_role=msg_data.get("subscriberRole", ""),
                is_delete=notify.get("isDelete", False),
                is_top=msg_data.get("top", False),
                view_count=notify.get("viewCount", 0),
                like_count=notify.get("likeCount", 0),
                comment_count=notify.get("commentCount", 0)
            ))
        
        # 解析分页信息
        page_info_data = data.get("pageInfo", {})
        page_info = MessagePageInfo(
            current_page=page_info_data.get("currentPage", 1),
            page_size=page_info_data.get("pageSize", page_size),
            total_count=page_info_data.get("totalCount", 0),
            total_page=page_info_data.get("totalPage", 1),
            first_page=page_info_data.get("firstPage", 1),
            last_page=page_info_data.get("lastPage", 1),
            next_page=page_info_data.get("nextPage", 2),
            prev_page=page_info_data.get("prevPage", 1),
            all_pages=page_info_data.get("allPages", [])
        )
        
        return PersonalMessageList(
            messages=ExtendedList(messages),
            page_info=page_info,
            total_count=pager_messages.get("totalCount", 0)
        )

    def send_personal_message(
        self,
        receiver_id: str,
        content: str
    ) -> bool:
        """发送私信消息
        
        Args:
            receiver_id (str): 接收者用户ID
            content (str): 消息内容
        
        Returns:
            bool: 发送是否成功
        """
        r = self._session.post(
            f"{Url.SEND_PERSONAL_MESSAGE}?_t={int(time.time() * 1000)}",
            data={
                "receiverId": receiver_id,
                "content": content,
                "type": "personalMsg"
            }
        )
        data = r.json()
        return data.get("result") == "success"
T = TypeVar("T")


class ExtendedList(List[T]):
    """扩展列表, 方便找到列表里的元素"""

    def __init__(self, ls: Optional[List[T]] = None):
        super().__init__(list() if ls is None else ls)

    def foreach(self, f: Callable[[T], None]):
        for each in self:
            f(each)

    def find(self, f: Callable[[T], bool]) -> Optional[T]:
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

    def find_by_name(self, name: str) -> Optional[T]:
        """返回列表里第一个特定名字的元素, 没有则返回None"""
        return self.find(lambda d: d.name == name) # type: ignore

    def find_all_by_name(self, name: str) -> "ExtendedList[T]":
        """返回列表里所有特定名字的元素"""
        return self.find_all(lambda d: d.name == name) # type: ignore

    def find_by_id(self, spec_id: str) -> Optional[T]:
        """返回列表里第一个特定id的元素, 没有则返回None"""
        return self.find(lambda d: d.id == spec_id) # type: ignore

    def find_all_by_id(self, spec_id: str) -> "ExtendedList[T]":
        """返回列表里所有特定id的元素"""
        return self.find_all(lambda d: d.id == spec_id) # type: ignore



@dataclass
class AcademicYear:
    """学年"""

    name: str = ""
    code: str = ""
    begin_time: str = ""
    end_time: str = ""

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
        return type(other) is type(self) and other.id == self.id

    def __str__(self):
        return f"学校: {self.school} 年级: {self.grade.name} 班级: {self.name}"


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
    exam_id: str = field(default="", repr=False)
    create_user: Person = field(default_factory=Person, repr=False)
    create_time: float = field(default=0, repr=False)

    def __eq__(self, other):
        return type(other) is type(self) and other.id == self.id


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
    subjects: ExtendedList[Subject] = field(default_factory=ExtendedList, repr=False)  # type: ignore # 总考试科目(不同班级实际考试科目可能只有部分)
    clazzs: ExtendedList[StuClass] = field(default_factory=ExtendedList, repr=False)  # type: ignore # 参考班级
    schools: ExtendedList[School] = field(default_factory=ExtendedList, repr=False)     # type: ignore # 参考学校
    create_user: Person = field(default_factory=Person, repr=False)
    create_time: float = field(default=0, repr=False)
    class_rank: int = field(default=0, repr=False)
    grade_rank: int = field(default=0, repr=False)
    academic_year: AcademicYear = field(default_factory=AcademicYear, repr=False)
    is_final: bool = False

    def __bool__(self):
        return bool(self.id)

    def __eq__(self, other):
        return type(other) is type(self) and other.id == self.id


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
            self, ls: Optional[list] = None, exam: Optional[Exam] = None, person: Optional[StuPerson] = None
    ):

        super().__init__([] if ls is None else ls)
        self.exam = exam if exam is not None else Exam()
        self.person = person if person is not None else StuPerson()

    def __repr__(self):
        if self.exam and self.person:
            msg = f"{self.person.name}-{self.exam.name}\n" + "".join(
                [f"{subject}\n" for subject in self]
            )
            return msg[:-1]
        return super().__repr__()

    def __str__(self):
        return self.__repr__()


@dataclass
class MarkingRecord:
    """批改记录"""

    time: datetime
    score: float


@dataclass
class SubTopicRecord:
    """小题得分详情"""

    score: float
    marking_records: Optional[ExtendedList[MarkingRecord]]


@dataclass
class TopicRecord:
    """题目得分详情"""

    title: str
    score: float
    standard_score: float
    subtopic_records: Optional[ExtendedList[SubTopicRecord]]


class AnswerRecord(ExtendedList[TopicRecord]):
    """一场考试的得分详情"""


@dataclass
class HwType:
    """作业类型, eg: 105 自由出题"""

    name: str = ""
    code: int = 0


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


@dataclass
class MessageUser:
    """消息用户信息"""
    user_id: str = ""
    user_name: str = ""
    role: str = ""
    school_id: str = ""
    area_id: str = ""
    city_id: str = ""
    country_id: str = ""
    province_id: str = ""


@dataclass
class PersonalMessage:
    """私信消息"""
    id: int
    """消息ID"""
    content: str
    """消息内容"""
    create_time: int
    """创建时间（毫秒时间戳）"""
    update_time: int
    """更新时间（毫秒时间戳）"""
    send_user_id: str
    """发送者用户ID"""
    sender: MessageUser
    """发送者信息"""
    notify_id: int
    """通知ID"""
    subscriber: str = ""
    """订阅者ID"""
    subscriber_name: str = ""
    """订阅者名称"""
    subscriber_role: str = ""
    """订阅者角色"""
    is_delete: bool = False
    """是否删除"""
    is_top: bool = False
    """是否置顶"""
    view_count: int = 0
    """查看次数"""
    like_count: int = 0
    """点赞数"""
    comment_count: int = 0
    """评论数"""
    
    def get_create_datetime(self) -> datetime:
        """获取创建时间的datetime对象"""
        return datetime.fromtimestamp(self.create_time / 1000)
    
    def get_update_datetime(self) -> datetime:
        """获取更新时间的datetime对象"""
        return datetime.fromtimestamp(self.update_time / 1000)


@dataclass
class MessagePageInfo:
    """分页信息"""
    current_page: int
    """当前页"""
    page_size: int
    """每页大小"""
    total_count: int
    """总数"""
    total_page: int
    """总页数"""
    first_page: int
    """首页"""
    last_page: int
    """末页"""
    next_page: int
    """下一页"""
    prev_page: int
    """上一页"""
    all_pages: List[int] = field(default_factory=list)
    """所有页码列表"""


@dataclass
class PersonalMessageList:
    """私信消息列表"""
    messages: ExtendedList[PersonalMessage]
    """消息列表"""
    page_info: MessagePageInfo
    """分页信息"""
    total_count: int
    """总数"""
    
    def get_unread_messages(self) -> ExtendedList[PersonalMessage]:
        """获取未读消息列表（根据view_count判断）"""
        return self.messages.find_all(lambda m: m.view_count == 0)
    
    def get_messages_by_sender(self, sender_id: str) -> ExtendedList[PersonalMessage]:
        """获取指定发送者的消息列表"""
        return self.messages.find_all(lambda m: m.send_user_id == sender_id)
