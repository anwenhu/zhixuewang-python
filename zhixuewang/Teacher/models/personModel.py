from zhixuewang.models.personModel import Person, StuClass, Sex, School
from zhixuewang.models.basicModel import ExtendedList

class TeaPerson(Person):
    def __init__(self,
                name: str, 
                id: str, 
                gender: Sex, 
                email: str, 
                mobile: str,
                qq_number: str, 
                birthday: int, 
                avatar: str,
                code: str,
                clazz: StuClass):
        super(StuPerson, self).__init__(name, id, gender, email, mobile, qq_number, birthday, avatar)
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
