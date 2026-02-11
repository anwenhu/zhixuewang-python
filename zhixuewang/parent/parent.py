from typing import Union

from typing_extensions import deprecated

from zhixuewang.models import (
    ExtendedList,
    Role,
    StuClass,
    StuPerson,
)
from zhixuewang.student.student import StudentAccount


class ParentAccount(StudentAccount):
    """家长账号"""

    def __init__(self, session):
        super().__init__(session)
        self.role = Role.parent

    def to_student(self) -> StudentAccount:
        raise NotImplementedError("ParentAccount无法转换为StudentAccount")
    
    def to_parent(self) -> "ParentAccount":
        """将Account转换为ParentAccount"""
        return self
    
    @deprecated("家长账户无法获取基本信息")
    def set_base_info(self):
        raise NotImplementedError("家长账户无法获取基本信息")

    @deprecated("家长账户无法获取同班同学列表")
    def get_classmates(self, clazz_data: Union[StuClass, str] = "") -> ExtendedList[StuPerson]:
        raise NotImplementedError("家长账户无法获取同班同学列表")
    
    @deprecated("家长账户无法获取班级列表")
    def get_clazzs(self) -> ExtendedList[StuClass]:
        raise NotImplementedError("家长账户无法获取班级列表")
    
    @deprecated("家长账户无法获取班级信息")
    def get_clazz(self, clazz_data: Union[StuClass, str] = "") -> StuClass | None:
        raise NotImplementedError("家长账户无法获取班级信息")
   