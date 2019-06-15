import time
from .models.personModel import *
from .models.urlModel import *
class Person:
    def __init__(self, __session):
        self.__session = __session

    def get_user_id(self, name: str) -> str:
        """
        转换名字为id
        :param name:
        :return:
        """
        classmates = self.get_classmates()
        for classmate in classmates:
            if classmate.name == name:
                return classmate.userId
        return ""

    def get_classmates(self, class_: classDataModel = None) -> list:
        """
        返回年级里指定班级里学生列表和朋友列表
        默认返回本班
        :param self:
        :return:
        """
        classmates = list()
        if class_ == None:
            r = self.__session.get(f"{GET_FRIEND_URL}?d={int(time.time())}")
            data = r.json()
            for each in data["studentList"]:
                classmates.append(personDataModel(
                    userName=each["name"], 
                    userId=each["id"]
                ))
        else:
            class_id = class_.classId
            p = {"classId": class_id}
            r = self.__session.get(GET_CLASSMATES_URL, params=p)
            for each in r.json():
                classmates.append(personDataModel(
                    userName=each["name"], 
                    userId=each["id"]
                ))
        return classmates

    def get_friends(self) -> list:
        friends = []
        json_data = self.__session.get(
            f"{GET_FRIEND_URL}?d={int(time.time())}") \
            .json()
        for each in json_data["friendList"]:
            friends.append(personDataModel(
                userName=each["friendName"],
                userId=each["friendId"]
            ))

        return friends

    def invite_friend(self, user_id: str) -> str:
        """
        邀请朋友
        :param user_id:用户id
        :return:
        """
        p = {
            "friendId": user_id,
            "isTwoWay": "true"
        }
        r = self.__session.get(f"{INVITE_FRIEND_URL}?d={int(time.time())}", params=p)
        json = r.json()
        if json["result"] == "success":
            return "success"
        elif json["message"] == "已发送过邀请，等待对方答复":
            return "已发送过邀请，等待对方答复"
        else:
            return ""

    def remove_friend(self, user_id: str) -> bool:
        """
        删除朋友
        :param user_id:用户id可以通过getUserId获取
        :return:
        """
        p = {"friendId": user_id}
        r = self.__session.get(f"{DELETE_FRIEND_URL}?d={int(time.time())}", params=p)
        if r.json()["result"] != "success":
            return False
        else:
            return True

    def get_clazzs(self) -> list:
        l = list()
        r = self.__session.get(f"{GET_CLAZZS_URL}?d={int(time.time())}")
        json = r.json()
        for each in json["clazzs"]:
            l.append(classDataModel(
                className=each["name"],
                classId=each["id"]
            ))
        return l
    