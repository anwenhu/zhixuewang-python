import time
from .models.personModel import *

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

    def get_classmates(self) -> list:
        """
        返回班级里学生列表和朋友列表
        :param self:
        :return:
        """
        classmates = list()
        data = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/friendmanage/?d=%d" % int(time.time()))
        data = data.json()
        for each in data["studentList"]:
            classmates.append(personDataModel(
                userName=each["name"], 
                userId=each["id"]
            ))
        return classmates

    def get_friends(self) -> list:
        friends = []
        json_data = self.__session.get(
            "http://www.zhixue.com/zhixuebao/zhixuebao/friendmanage/?d=%d" % int(time.time())) \
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
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/addFriend/?d=%d" % int(time.time()), params=p)
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
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/delFriend/?d=%d" % int(time.time()), params=p)
        if r.json()["result"] != "success":
            return False
        else:
            return True
