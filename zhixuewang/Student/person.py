from zhixuewang.models.personModel import StuClass, School, Sex
from zhixuewang.Student.models.personModel import StuPerson, StuPersonList
from zhixuewang.models.basicModel import ExtendedList
from zhixuewang.Student.models.urlModel import (GET_FRIEND_URL, GET_CLASSMATES_URL,
                              INVITE_FRIEND_URL, DELETE_FRIEND_URL, GET_CLAZZS_URL, GET_TEACHERS_URL)
import time
from enum import IntEnum
from typing import List

class FriendMsg(IntEnum):
    SUCCESS = 200          # 邀请成功
    ALREADY = 201          # 已发送过邀请，等待对方答复
    UNDEFINED = 202        # 未知错误

class ExtraPerson:
    def get_clazzs(self) -> List[StuClass]:
        """
        获取当前年级所有班级
        :return:
        """
        clazzs = ExtendedList()
        r = self._session.get(GET_CLAZZS_URL, params={
            "d": int(time.time())
        })
        json_data = r.json()
        for clazz in json_data["clazzs"]:
            clazzs.append(StuClass(
                name=clazz["name"],
                id=clazz["id"],
                grade=self.clazz.grade,
                school=self.clazz.school
            ))
        return clazzs
    
    def get_clazz(self, clazz_data: StuClass or str = None):
        """
        获取当前年级班级
        :param clazz_data:
            可以为班级id或班级名称
            为StuClass实例时直接返回
            为空时返回自己班级
        :return:
        """
        if not clazz_data:
            return self.clazz
        if type(clazz_data) == StuClass:
            return clazz_data
        clazzs = self.get_clazzs()
        if clazz_data.isdigit(): # 判断为id还是名称
            clazz = clazzs.find_by_id(clazz_data)   # 为id
        else:
            clazz = clazzs.find_by_name(clazz_data)  # 为名称
        return clazz

    def __get_classmates(self, clazz_id: str) -> List[StuPerson]:
        classmates = StuPersonList()
        r = self._session.get(GET_CLASSMATES_URL, params={
            "r": f"{self.id}student",
            "clazzId": clazz_id
        })
        json_data = r.json()
        for classmate in json_data:
            birthday = int(classmate.get("birthday", 0)) / 1000
            classmates.append(StuPerson(
                name=classmate["name"],
                id=classmate["id"],
                birthday=birthday,
                clazz=StuClass(
                    id=classmate["clazz"]["id"],
                    name=classmate["clazz"]["name"],
                    grade=self.clazz.grade,
                    school=School(
                        id=classmate["clazz"]["school"]["id"],
                        name=classmate["clazz"]["school"]["name"]
                    )
                ),
                code=classmate["code"],
                email=classmate["email"],
                qq_number=classmate["im"],
                gender=Sex.BOY if classmate["gender"] == "1" else Sex.GIRL,
                mobile=classmate["mobile"]
            ))
        return classmates

    def get_classmates(self, clazz_data: StuClass or str = None) -> List[StuPerson]:
        """
        获取指定班级里学生列表
        :param clazz_data:
            可以为班级id或班级名称或StuClass实例
            为空时获取本班学生列表
        :return:
        """
        clazz = self.get_clazz(clazz_data)
        if clazz is None:
            return None
        return self.__get_classmates(clazz.id)
        

    def get_friends(self) -> List[StuPerson]:
        """
        获取朋友列表
        :return:
        """
        friends = StuPersonList()
        r = self._session.get(GET_FRIEND_URL, params={
            "d": int(time.time())
        })
        json_data = r.json()
        for friend in json_data["friendList"]:
            friends.append(StuPerson(
                name=friend["friendName"],
                id=friend["friendId"]
            ))
        return friends


    def invite_friend(self, friend: StuPerson or str) -> FriendMsg:
        """
        邀请朋友
        :param friend:
            StuPerson的实例或用户id
        :return:
        """
        user_id = friend
        if type(friend) == StuPerson:
            user_id = friend.id
        r = self._session.get(INVITE_FRIEND_URL, params={
            "d": int(time.time()),
            "friendId": user_id,
            "isTwoWay": "true"
        })
        json_data = r.json()
        if json_data["result"] == "success":
            return FriendMsg.SUCCESS
        elif json_data["message"] == "已发送过邀请，等待对方答复":
            return FriendMsg.ALREADY
        else:
            return FriendMsg.UNDEFINED


    def remove_friend(self, friend: StuPerson or str) -> bool:
        """
        删除朋友
        :param friend:
            StuPerson的实例或用户id
        :return:
        """
        r = self._session.get(DELETE_FRIEND_URL, params={
            "d": int(time.time()),
            "friendId": user_id
        })
        return r.json()["result"] == "success"


    


# def get_teachers(self) -> list:
#     r = self._session.get(GET_TEACHERS_URL, params={
#         "r": f"{self.id}student"
#     })
#     json_obj = r.json()
#     teachers = personsModel(list())
#     for teacher in json_obj:
#         b = int(teacher["birthday"]) / \
#             1000 if teacher.get("birthday") else 0
#         teachers.append(personModel(
#             name=teacher["name"],
#             id=teacher["id"],
#             birthday=b if b > 0 else 0,
#             login=teacher["code"],
#             email=teacher["email"],
#             qq_number=teacher["im"],
#             gender="男" if teacher["gender"] == "1" else "女",
#             mobile=teacher.get("mobile"),
#         ))
#     return teachers
