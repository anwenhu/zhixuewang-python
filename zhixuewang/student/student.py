import hashlib
import json
import time
import uuid
from enum import IntEnum
from typing import List, Union
from zhixuewang.models import (ExtendedList, Exam, Mark, Subject, SubjectScore,
                               StuClass, School, Sex, Grade, Phase, ExtraRank)
from zhixuewang.exceptions import UserDefunctError
from zhixuewang.student.models import StuPerson, StuPersonList
from zhixuewang.student.urls import Url


def _check_is_uuid(msg: str):
    """判断msg是否为uuid"""
    return len(msg) == 36 and msg[14] == "4" and msg[8] == msg[13] == msg[18] == msg[23] == "-"


def _md5_encode(msg: str) -> str:
    md5 = hashlib.md5()
    md5.update(msg.encode(encoding="utf-8"))
    return md5.hexdigest()


class FriendMsg(IntEnum):
    SUCCESS = 200  # 邀请成功
    ALREADY = 201  # 已发送过邀请，等待对方答复
    UNDEFINED = 202  # 未知错误


class Student(StuPerson):
    """学生账号"""

    def __init__(self, session):
        super().__init__()
        self._session = session
        self.username = ""
        self.role = "student"
        self.token_timestamp = ["", 0]

    def __get_auth_header(self) -> dict:
        """获取header"""
        auth_guid = str(uuid.uuid4())
        auth_time_stamp = str(int(time.time() * 1000))
        auth_token = _md5_encode(auth_guid + auth_time_stamp +
                                 "iflytek!@#123student")
        token, cur_time = self.token_timestamp
        if token and time.time() - cur_time < 600:  # 判断token是否过期
            return {
                "authbizcode": "0001",
                "authguid": auth_guid,
                "authtimestamp": auth_time_stamp,
                "authtoken": auth_token,
                "XToken": token
            }
        r = self._session.get(Url.XTOKEN_URL,
                              headers={
                                  "authbizcode": "0001",
                                  "authguid": auth_guid,
                                  "authtimestamp": auth_time_stamp,
                                  "authtoken": auth_token
                              })
        if r.json()["errorCode"] != 0:
            raise Exception(r.json()["errorInfo"])
        self.token_timestamp[0] = r.json()["result"]
        self.token_timestamp[1] = time.time()
        return self.__get_auth_header()

    def set_base_info(self):
        """设置账户基本信息, 如用户id, 姓名, 学校等"""
        r = self._session.get(Url.INFO_URL)
        json_data = r.json()["student"]
        if not json_data.get("clazz", False):
            raise UserDefunctError()
        self.code = json_data.get("code")
        self.name = json_data.get("name")
        self.avatar = json_data.get("avatar")
        self.gender = Sex.BOY if json_data.get("gender") == "1" else Sex.GIRL
        self.username = json_data.get("loginName")
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.email = json_data.get("email")
        self.qq_number = json_data.get("im")
        self.clazz = StuClass(
            id=json_data["clazz"]["id"],
            name=json_data["clazz"]["name"],
            school=School(
                id=json_data["clazz"]["division"]["school"]["id"],
                name=json_data["clazz"]["division"]["school"]["name"]),
            grade=Grade(code=json_data["clazz"]["division"]["grade"]["code"],
                        name=json_data["clazz"]["division"]["grade"]["name"],
                        phase=Phase(code=json_data["clazz"]["division"]
                        ["grade"]["phase"]["code"],
                                    name=json_data["clazz"]["division"]
                                    ["grade"]["phase"]["name"])))
        self.birthday = json_data.get("birthday", 0)
        return self

    def get_exam(self, exam_data: Union[Exam, str] = None) -> Exam:
        """获取考试

        Args:
            exam_data (Union[Exam, str]): 考试id 或 考试名称, 为Exam实例时直接返回, 为默认值时返回最新考试

        Returns:
            Exam
        """
        if not exam_data:
            return self.get_latest_exam()
        if isinstance(exam_data, Exam):
            if not exam_data:
                return self.get_latest_exam()
            elif exam_data.classRank and exam_data.gradeRank:
                return exam_data
            else:
                return self.get_exams().find_by_id(exam_data.id)
        if _check_is_uuid(exam_data):
            exams = self.get_exams()
            exam = exams.find_by_id(exam_data)  # 为id
        else:
            exams = self.get_exams()
            exam = exams.find_by_name(exam_data)
        return exam

    def __get_page_exam(self, page_index: int) -> ExtendedList[Exam]:
        """获取指定页数的考试列表"""
        exams = ExtendedList()
        r = self._session.get(Url.GET_EXAM_URL,
                              params={
                                  "actualPosition": "0",
                                  "pageIndex": page_index,
                                  "pageSize": 10
                              })
        json_data = r.json()
        for exam_data in json_data["examList"]:
            exam = Exam(
                id=exam_data["examId"],
                name=exam_data["examName"],
                grade_code=exam_data["gradeCode"],
                subject_codes=exam_data["subjectCodes"],
                classRank=exam_data.get("customClassRank"),
                gradeRank=exam_data.get("customSchoolRank")
            )
            exam.create_time = exam_data["examCreateDateTime"]
            exam.exam_time = exam_data["examDateTime"] if exam_data["examDateTime"] else 0
            exams.append(exam)
        return exams

    def get_latest_exam(self) -> Exam:
        """获取最新考试"""
        exams = self.__get_page_exam(1)
        return exams[0] if exams else None

    def get_exams(self) -> ExtendedList[Exam]:
        """获取所有考试"""
        exams = ExtendedList()
        i = 1
        check = True
        while check:
            cur_exams = self.__get_page_exam(i)
            exams.extend(cur_exams)
            check = len(cur_exams) > 0
            i += 1
        return exams

    def __get_self_mark(self, exam: Exam, has_total_score: bool) -> Mark:
        mark = Mark(exam=exam, person=self)
        r = self._session.get(Url.GET_MARK_URL,
                              params={"examId": exam.id},
                              headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        json_data = json_data["result"]
        # exam.name = json_data["total_score"]["examName"]
        # exam.id = json_data["total_score"]["examId"]
        for subject in json_data["paperList"]:
            subject_score = SubjectScore(
                score=subject["userScore"],
                subject=Subject(
                    id=subject["paperId"],
                    name=subject["subjectName"],
                    code=subject["subjectCode"],
                    standard_score=subject["standardScore"],
                    exam=exam),
                person=StuPerson()
            )
            # subject_score.create_time = 0
            mark.append(subject_score)
        total_score = json_data.get("totalScore")
        if has_total_score and total_score:
            subject_score = SubjectScore(
                score=total_score["userScore"],
                subject=Subject(
                    id="",
                    name=total_score["subjectName"],
                    code="99",
                    standard_score=total_score["standardScore"],
                    exam=exam,
                ),
                person=StuPerson(),
                class_rank=ExtraRank(rank=exam.classRank),
                grade_rank=ExtraRank(rank=exam.gradeRank)
            )
            # subject_score.create_time = 0
            mark.append(subject_score)
        return mark

    def get_self_mark(self,
                      exam_data: Union[Exam, str] = None,
                      has_total_score: bool = True) -> Mark:
        """获取指定考试的成绩

        Args:
            exam_data (Union[Exam, str]): 考试id 或 考试名称 或 Exam实例, 默认值为最新考试
            has_total_score (bool): 是否计算总分, 默认为True

        Returns:
            Mark
        """
        exam = self.get_exam(exam_data)
        if exam is None:
            return Mark()
        return self.__get_self_mark(exam, has_total_score)

    def __get_subjects(self, exam: Exam) -> ExtendedList[Subject]:
        subjects = ExtendedList()
        r = self._session.get(Url.GET_SUBJECT_URL,
                              params={"examId": exam.id},
                              headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        for subject in json_data["result"]["paperList"]:
            subjects.append(
                Subject(id=subject["paperId"],
                        name=subject["subjectName"],
                        code=subject["subjectCode"],
                        standard_score=subject["standardScore"],
                        exam=exam))
        return subjects

    def get_subjects(self, exam_data: Union[Exam, str] = None) -> ExtendedList[Subject]:
        """获得指定考试的所有学科(不算总分)

        Args:
            exam_data (Union[Exam, str]): 考试id 或 考试名称 或 Exam实例, 默认值为最新考试

        Returns:
            ExtendedList[Subject]
        """
        exam = self.get_exam(exam_data)
        if exam is None:
            return ExtendedList([])
        return self.__get_subjects(exam)

    def __get_subject(self, exam: Exam, subject_data: str):
        subjects = self.get_subjects(exam)
        if _check_is_uuid(subject_data):  # 判断为id还是名称
            subject = subjects.find_by_id(subject_data)  # 为id
        else:
            subject = subjects.find_by_name(subject_data)  # 为名称
        return subject

    def get_subject(self,
                    subject_data: Union[Subject, str],
                    exam_data: Union[Exam, str] = None) -> Subject:
        """获取指定考试的学科

        Args:
            subject_data (Union[Subject, str]): 学科id 或 学科名称, 为Subject实例时直接返回
            exam_data (Union[Exam, str]): 考试id 或 考试名称 或 Exam实例, 默认值为最新考试

        Returns:
            Subject
        """
        if isinstance(subject_data, Subject):
            return subject_data
        exam = self.get_exam(exam_data)
        if exam is None:
            return Subject()
        return self.__get_subject(exam, subject_data)

    def __get_original(self, subject_id: str, exam_id: str) -> ExtendedList[str]:
        r = self._session.get(Url.GET_ORIGINAL_URL,
                              params={
                                  "examId": exam_id,
                                  "paperId": subject_id,
                              },
                              headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        image_urls = ExtendedList()
        for image_url in json.loads(json_data["result"]["sheetImages"]):
            image_urls.append(image_url)
        return image_urls

    def get_original(self,
                     subject_data: Union[Subject, str],
                     exam_data: Union[Exam, str] = None) -> List[str]:
        """获得指定考试学科的原卷地址

        Args:
            subject_data (Union[Subject, str]): 学科id 或 学科名称 或 Subject实例
            exam_data (Union[Exam, str]): 考试id 或 考试名称, 默认为最新考试

        Returns:
            List[str]: 原卷地址的列表
        """
        exam = self.get_exam(exam_data)
        if not exam:
            return []
        subject = self.get_subject(subject_data)
        if not subject:
            return []
        return self.__get_original(subject.id, exam.id)

    def get_clazzs(self) -> ExtendedList[StuClass]:
        """获取当前年级所有班级"""
        clazzs = ExtendedList()
        r = self._session.get(Url.GET_CLAZZS_URL,
                              params={"d": int(time.time())})
        json_data = r.json()
        for clazz in json_data["clazzs"]:
            clazzs.append(
                StuClass(name=clazz["name"],
                         id=clazz["id"],
                         grade=self.clazz.grade,
                         school=self.clazz.school))
        return clazzs

    def get_clazz(self, clazz_data: Union[StuClass, str] = None) -> StuClass:
        """获取当前年级班级

        Args:
            clazz_data (Union[StuClass, str]): 班级id 或 班级名称, 为StuClass实例时直接返回, 为空时返回自己班级

        Returns:
            StuClass
        """
        if not clazz_data:
            return self.clazz
        if isinstance(clazz_data, StuClass):
            return clazz_data
        clazzs = self.get_clazzs()
        if clazz_data.isdigit():  # 判断为id还是名称
            clazz = clazzs.find_by_id(clazz_data)  # 为id
        else:
            clazz = clazzs.find_by_name(clazz_data)  # 为名称
        return clazz

    def __get_classmates(self, clazz_id: str) -> ExtendedList[StuPerson]:
        classmates = StuPersonList()
        r = self._session.get(Url.GET_CLASSMATES_URL,
                              params={
                                  "r": f"{self.id}student",
                                  "clazzId": clazz_id
                              })
        json_data = r.json()
        for classmate_data in json_data:
            birthday = int(int(classmate_data.get("birthday", 0)) / 1000)
            classmate = StuPerson(
                name=classmate_data["name"],
                id=classmate_data["id"],
                clazz=StuClass(
                    id=classmate_data["clazz"]["id"],
                    name=classmate_data["clazz"]["name"],
                    grade=self.clazz.grade,
                    school=School(
                        id=classmate_data["clazz"]["school"]["id"],
                        name=classmate_data["clazz"]["school"]["name"])),
                code=classmate_data.get("code"),
                email=classmate_data["email"],
                qq_number=classmate_data["im"],
                gender=Sex.BOY if classmate_data["gender"] == "1" else Sex.GIRL,
                mobile=classmate_data["mobile"])
            classmate.birthday = birthday
            classmates.append(classmate)
        return classmates

    def get_classmates(self, clazz_data: Union[StuClass, str] = None) -> ExtendedList[StuPerson]:
        """获取指定班级里学生列表

        Args:
            clazz_data (Union[StuClass, str]): 班级id 或 班级名称 或 StuClass实例, 为空时获取本班学生列表

        Returns:
            ExtendedList[StuPerson]
        """
        clazz = self.get_clazz(clazz_data)
        if clazz is None:
            return ExtendedList([])
        return self.__get_classmates(clazz.id)

    def get_friends(self) -> ExtendedList[StuPerson]:
        """获取朋友列表"""
        friends = StuPersonList()
        r = self._session.get(Url.GET_FRIEND_URL,
                              params={"d": int(time.time())})
        json_data = r.json()
        for friend in json_data["friendList"]:
            friends.append(
                StuPerson(name=friend["friendName"], id=friend["friendId"]))
        return friends

    def invite_friend(self, friend: Union[StuPerson, str]) -> FriendMsg:
        """邀请朋友

        Args:
            friend (Union[StuPerson, str]): 用户id 或 StuPerson的实例

        Returns:
            FriendMsg
        """
        user_id = friend
        if isinstance(friend, StuPerson):
            user_id = friend.id
        r = self._session.get(Url.INVITE_FRIEND_URL,
                              params={
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

    def remove_friend(self, friend: Union[StuPerson, str]) -> bool:
        """删除朋友

        Args:
            friend (Union[StuPerson, str]): 用户id 或 StuPerson的实例

        Returns:
            bool: True 表示删除成功, False 表示删除失败
        """
        user_id = friend
        if isinstance(friend, StuPerson):
            user_id = friend.id
        r = self._session.get(Url.DELETE_FRIEND_URL,
                              params={
                                  "d": int(time.time()),
                                  "friendId": user_id
                              })
        return r.json()["result"] == "success"
