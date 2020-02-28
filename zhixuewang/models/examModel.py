from zhixuewang.models.personModel import Person, School
from zhixuewang.models.basicModel import ExtendedList
from typing import List

class Exam:
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
        self.create_time = create_time
        self.exam_time = exam_time
        self.complete_time = complete_time
        self.status = status
        self.grade_code = grade_code
        self.subject_codes = subject_codes
        self.schools = schools
        self.create_school = create_school
    
    def __repr__(self):
        return f"Exam(id={self.id}, name={self.name})"
    
    def __str__(self):
        return self.__repr__()
    
    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id

class Subject:
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
        if create_user is None:
            create_user = Person()
        self.create_user = create_user
        self.create_time = create_time
        self.standard_score = standard_score
        if exam is None:
            exam = Exam()
        self.exam = exam
    
    def __repr__(self):
        return f"Subject(id={self.id}, name={self.name}, code={self.code}, exam={self.exam})"
    
    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return type(other) == type(self) and self.id == other.id

class ExtraRank:
    def __init__(self,
                avgScore: float = 0, 
                highScore: float = 0, 
                rank: int = 0 , 
                lowScore: float = 0):
        self.avgScore = avgScore
        self.highScore = highScore
        self.rank = rank
        self.lowScore = lowScore

    def __bool__(self):
        return bool(self.avgScore or self.highScore or self.rank or self.lowScore)

    def __repr__(self):
        return f"ExtraRank(avgScore={self.avgScore}, highScore={self.highScore}, rank={self.rank}, lowScore={self.lowScore})"
    
    def __str__(self):
        msg = ""
        if not self:
            return msg
        if self.avgScore:
            msg += f"平均分: {self.avgScore}\n"
        if self.highScore:
            msg += f"最高分: {self.highScore}\n"
        if self.lowScore:
            msg += f"最低分: {self.lowScore}\n"
        if self.rank:
            msg += f"排名: {self.rank}\n"
        return msg[:-1]

class SubjectScore:
    def __init__(self,
                score: float,
                classRank: ExtraRank = None,
                gradeRank: ExtraRank = None,
                subject: Subject = None,
                person: Person = None,
                create_time: int = 0):
        self.score = score
        if classRank is None:
            classRank = ExtraRank()
        self.classRank = classRank
        if gradeRank is None:
            gradeRank = ExtraRank()
        self.gradeRank = gradeRank
        self.subject = subject
        self.person = person
        self.create_time = create_time

    def __repr__(self):
        return f"SubjectScore(score={self.score}, classRank={self.classRank}, gradeRank={self.gradeRank}, subject={self.subject}, person={self.person})"

    def __str__(self):
        msg = f"{self.person.name} {self.subject.name}:\n分数: {self.score}\n"
        if self.classRank:
            msg += f"班级:\n{self.classRank}\n"
        if self.gradeRank:
            msg += f"年级:\n{self.gradeRank}\n"
        return msg[:-1]


class Mark(ExtendedList):
    def __init__(self, l: list = None, exam: Exam = None):
        super(Mark, self).__init__(l)
        self.exam = exam

    def __repr__(self):
        msg = ""
        for subject in self:
            msg += str(subject) + "\n"
        return msg[:-1]
        
    def __str__(self):
        return self.__repr__()