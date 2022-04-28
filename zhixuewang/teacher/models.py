from dataclasses import field, dataclass
from enum import Enum
from typing import Dict, List, Union
import copy
from zhixuewang.models import BasicSubject, Exam, ExtendedList, Person, School, StuClass, Sex, StuPerson, Subject, SubjectScore
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

class PersonScores(ExtendedList[SubjectScore]):
    """某人分数"""
    def __init__(self, l: List[SubjectScore]):
        super().__init__(l)
    
    def resolve(self) -> None:
        self.subject_map = {each.subject.name: i for i, each in enumerate(self)}

    def get_score(self, subject_name: str) -> SubjectScore:
        """获取分数
        Args:
            subject_name (str): 科目名称

        Returns:
            SubjectScore
        """
        return self[self.subject_map[subject_name]]

    

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

# class ClassScores(List[ExtendedList[SubjectScore]]):
#     """班级某场考试分数"""
#     def __init__(self, l: List[ExtendedList[SubjectScore]]):
#         l = sorted(l, key=lambda t: t[0].subject.code, reverse=False)
#         self.subject_map = {each[0].subject.name: i for i, each in enumerate(l)}
#         temp_person_map: Dict[str, PersonScores] = {}
#         self.id_name_map: Dict[str, List[str]] = {}
#         for each_subject in l:
#             for each in each_subject:
#                 temp_person_map[each.person.id] = PersonScores([each])
#                 if self.subject_map[each.subject.name] == 0:
#                     if each.person.id not in self.id_name_map:
#                         self.id_name_map[each.person.id] = [each.person.name] 
#                     else:
#                         self.id_name_map[each.person.id].append(each.person.name)
        
#         super().__init__(l)
    
#     def get_subject_scores(self, subject_name: str) -> ExtendedList[SubjectScore]:
#         """获取某一科的分数"""
#         return self[self.subject_map[subject_name]]
    
#     def get_person_scores(self, person_name: str) -> PersonScores:
#         """获取某人分数"""
#         result = []
#         for each_person_id in self.id_name_map[person_name]:
#             result.extend(self.person_map[each_person_id])
#         return PersonScores(result)
    
#     def to_person_scores(self) -> ExtendedList[PersonScores]:
#         return ExtendedList(list(self.person_map.values()))

    
class Scores(ExtendedList[PersonScores]):
    def __init__(self, l: List[ExtendedList[SubjectScore]]):
        self.person_map: Dict[str, PersonScores] = {}
        self.name_id_map: Dict[str, List[str]] = {}
        for each_subject in l:
            for each in each_subject:
                if each.person.id not in self.person_map: # 可能有人没考第一科
                    self.person_map[each.person.id] = PersonScores([])
                self.person_map[each.person.id].append(each)
                if each.person.name not in self.name_id_map:
                    self.name_id_map[each.person.name] = [each.person.id] 
                elif each.person.id not in self.name_id_map[each.person.name]:
                    self.name_id_map[each.person.name].append(each.person.id)
        for each in self.person_map.values():
            each.resolve()
        result = ExtendedList(list(self.person_map.values()))
        super().__init__(sorted(result, key=lambda t: t[-1].score, reverse=True))

    def get_person_scores_by_id(self, id: str) -> "PersonScores":
        return self.person_map[id]

    def get_person_scores_by_name(self, name: str) -> List[PersonScores]:
        result = []
        for each_id in self.name_id_map[name]:
            result.append(self.person_map[each_id])
        return result

    def get_school_scores_by_name(self, school_name: str) -> "Scores":
        return Scores(list(filter(lambda t: t[0].person.clazz.school.name == school_name, self)))

    def get_school_scores_by_id(self, school_id: str) -> "Scores":
        return Scores(list(filter(lambda t: t[0].person.clazz.school.id == school_id, self)))

    def get_class_scores_by_name(self, class_name: str):
        return Scores(list(filter(lambda t: t[0].person.clazz.name == class_name, self)))

    def get_class_scores_by_id(self, class_id: str):
        return Scores(list(filter(lambda t: t[0].person.clazz.name == class_id, self)))


# 单科 班级分类
@dataclass()
class RankData:
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

@dataclass
class ExtraData:
    avg_score: float
    medium_score: float # 中位数
    pass_rate: float # 及格率
    excellent_rate: float # 优秀率(85%以上)
    perfect_rate: float # 满分率
    var: float # 方差

@dataclass
class ClassExtraData(ExtraData):
    class_id: str
    class_name: str

@dataclass
class SchoolExtraData(ExtraData):
    school_id: str
    school_name: str

@dataclass
class ExamSubjectExtraData:
    subject: Subject
    class_extra_data: ExtendedList[ClassExtraData]
    school_extra_data: ExtendedList[SchoolExtraData]
    exam_extra_data: ExtraData

class ExamExtraData(List[ExamSubjectExtraData]):
    pass