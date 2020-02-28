from zhixuewang.models.basicModel import ExtendedList
from typing import List
from enum import Enum

class Phase:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code

    def __repr__(self):
        return f"Phase(name={self.name}, code={self.code})"
    
    def __str__(self):
        return self.__repr__()
    
class Grade:
    def __init__(self, name: str, code: str, phase: Phase):
        self.name = name
        self.code = code
        self.phase = phase
    
    def __repr__(self):
        return f"Grade(name={self.name}, code={self.code}, phase={self.phase})"
    
    def __str__(self):
        return self.__repr__()

class School:
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
    GIRL = "女"
    BOY = "男"

class Person:
    def __init__(self,
                name: str = "", 
                id: str = "", 
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
        
        self.birthday = birthday
        
        self.avatar = avatar
    
    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, gender={self.gender})"
    
    def __str__(self):
        return self.__repr__()
    
class StuClass:
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

