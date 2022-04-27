from dataclasses import field, dataclass
from enum import Enum
from typing import Dict, List, Union

from zhixuewang.models import Exam, ExtendedList, Person, School, StuClass, Sex, Subject, SubjectScore
from zhixuewang.tools.rank import get_rank_map


class TeacherRole(Enum):
    TEACHER = "老师"
    HEADMASTER = "校长"

    def __str__(self):
        return self._value_


class TeaPerson(Person):
    def __init__(self,
                 name: str = "",
                 id: str = "",
                 gender: Sex = Sex.GIRL,
                 email: str = "",
                 mobile: str = "",
                 qq_number: str = "",
                 birthday: int = 0,
                 avatar: str = "",
                 code: str = "",
                 clazz: StuClass = None,
                 roles: List[TeacherRole] = [TeacherRole.TEACHER]):
        super().__init__(name, id, gender, email, mobile, qq_number, birthday,
                         avatar)
        self.code = code
        self.clazz = clazz


# class TeaPersonList(ExtendedList):
#     def find_by_code(self, code: str) -> StuPerson:
#         return self.find(lambda p: p.code == code)

#     def find_by_clazz_id(self, clazz_id: str) -> StuPerson:
#         return self.find(lambda p: p.clazz.id == clazz_id)

#     def find_by_clazz(self, clazz: StuClass) -> StuPerson:
#         return self.find(lambda p: p.clazz == clazz)

#     def find_by_school_id(self, school_id: str) -> StuPerson:
#         return self.find(lambda p: p.school.id == school_id)

#     def find_by_school(self, school: School) -> StuPerson:
#         return self.find(lambda p: p.school == school)

class ClassSubjectScores(ExtendedList[SubjectScore]):
    """班级单科分数"""
    def __init__(self, l: List[SubjectScore]):
        l = sorted(l, key=lambda t: t.score, reverse=True)
        rank_map = get_rank_map([i.score for i in l])
        for each in l:
            each.class_rank = rank_map[each.score]
        super().__init__(l)

    def get_person_score(self, name: str) -> Union[SubjectScore, None]:
        return self.find(lambda t: t.person.name == name)
    
    @property
    def avg_score(self) -> float:
        total_score = 0
        for each in self:
            total_score += each.score
        return total_score / len(self)
    
    @property
    def max_score(self) -> float:
        return self[0].score
    
    @property
    def min_score(self) -> float:
        return self[-1].score

class ClassScores(List[ExtendedList[SubjectScore]]):
    """班级某场考试分数"""
    def __init__(self, l: List[ExtendedList[SubjectScore]]):
        l = sorted(l, key=lambda t: t[0].subject.code, reverse=False)
        self.subject_map = {each[0].subject.name: i for i, each in enumerate(l)}
        self.person_map = {}
        self.id_name_map = {} #  重名时只获取第一个
        for each in l[0]:
            self.person_map[each.person.id] = [each]
            if each.person.id not in self.id_name_map:
                self.id_name_map[each.person.id] = [each.person.name] 
        for each_subject in l[1:]:
            for each in each_subject:
                self.person_map[each.person.id].append(each)
        
        super().__init__(l)
    
    def get_subject_scores(self, subject_name: str) -> ExtendedList[SubjectScore]:
        """获取某一科的分数"""
        return self[self.subject_map[subject_name]]
    
    def get_person_scores(self, person_name: str) -> ExtendedList[SubjectScore]:
        """获取默认分数"""
        return self.person_map[self.id_name_map[person_name]]


# 单科 班级分类
@dataclass()
class ExtraData:
    schoolRankMap: Dict[str, Dict[float, int]]
    # schoolId => classID => score => rank
    schoolsRankMap: Dict[str, Dict[str, Dict[float, int]]]
    # 总排名
    allRankMap: Dict[float, int]


@dataclass
class TopicTeacherMarkingProgress:
    teacher_name: str
    school: School
    is_online: bool
    teacher_code: str
    complete_count: int
    uncomplete_count: int
    complete_precent: float = 0
    
    @staticmethod
    def get_complete_precent(self) -> float:
        if self.complete_count == 0 and self.uncomplete_count == 0:
            return 100
        return (self.complete_count / (self.complete_count + self.uncomplete_count)) * 100

@dataclass
class TopicMarkingProgress:
    disp_title: str
    topic_number: int
    complete_precent: float 
    subject_id: str
    teachers: List[TopicTeacherMarkingProgress] = field(default_factory=list)

@dataclass
class SubjectMarkingProgress:
    subject: Subject
    markingProgresses: List[TopicMarkingProgress] = field(default_factory=list)

@dataclass
class ExamMarkingProgress:
    exam: Exam
    markingProgresses: List[SubjectMarkingProgress] = field(default_factory=list)