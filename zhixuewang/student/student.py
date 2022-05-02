import hashlib
import json
import math
import time
import uuid
from enum import IntEnum
from typing import List, Tuple, Union
from zhixuewang.models import (Account, BasicSubject, ErrorBookTopic, ExtendedList, Exam, Homework, HwAnsPubData, HwResource, HwType, Mark, Role, StuHomework, Subject, SubjectScore,
                               StuClass, School, Sex, Grade, Phase, ExamInfo,
                               StuPerson, StuPersonList)
from zhixuewang.exceptions import GetOriginalError, UserDefunctError, PageConnectionError, PageInformationError
from zhixuewang.student.urls import Url
from json import JSONDecodeError


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


class StudentAccount(Account, StuPerson):
    """学生账号"""

    def __init__(self, session):
        super().__init__(session, Role.student)
        self._token_timestamp = ["", 0]

    def _get_auth_header(self) -> dict:
        """获取header"""
        self.update_login_status()
        auth_guid = str(uuid.uuid4())
        auth_time_stamp = str(int(time.time() * 1000))
        auth_token = _md5_encode(auth_guid + auth_time_stamp +
                                 "iflytek!@#123student")
        token, cur_time = self._token_timestamp
        if token and time.time() - cur_time < 600:  # 判断token是否过期
            return {
                "authbizcode": "0001",
                "authguid": auth_guid,
                "authtimestamp": auth_time_stamp,
                "authtoken": auth_token,
                "XToken": token
            }
        r = self._session.get(Url.XTOKEN_URL, headers={
            "authbizcode": "0001",
            "authguid": auth_guid,
            "authtimestamp": auth_time_stamp,
            "authtoken": auth_token
        })
        if not r.ok:
            raise PageConnectionError(
                f"_get_auth_header中出错, 状态码为{r.status_code}")
        try:
            if r.json()["errorCode"] != 0:
                raise PageInformationError(
                    f"_get_auth_header出错, 错误信息为{r.json()['errorInfo']}")
            self._token_timestamp[0] = r.json()["result"]
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"_get_auth_header中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        self._token_timestamp[1] = time.time()
        return self._get_auth_header()

    def set_base_info(self):
        """设置账户基本信息, 如用户id, 姓名, 学校等"""
        self.update_login_status()
        r = self._session.get(Url.INFO_URL)
        if not r.ok:
            raise PageConnectionError(f"set_base_info出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()["student"]
            if not json_data.get("clazz", False):
                raise UserDefunctError()
            self.code = json_data.get("code")
            self.name = json_data.get("name")
            self.avatar = json_data.get("avatar")
            self.gender = Sex.BOY if json_data.get(
                "gender") == "1" else Sex.GIRL
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
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"set_base_info中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return self

    def get_exam(self, exam_data: Union[Exam, str] = "") -> Exam:
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
            elif exam_data.class_rank and exam_data.grade_rank:
                return exam_data
            else:
                return self.get_exams().find_by_id(exam_data.id)
        exams = self.get_exams()
        if _check_is_uuid(exam_data):
            exam = exams.find_by_id(exam_data)  # 为id
        else:
            exam = exams.find_by_name(exam_data)
        return exam

    def get_page_exam(self, page_index: int) -> Tuple[ExtendedList[Exam], bool]:
        """获取指定页数的考试列表"""
        self.update_login_status()
        exams: ExtendedList[Exam] = ExtendedList()
        r = self._session.get(Url.GET_EXAM_URL,
                              params={
                                  "pageIndex": page_index,
                                  "pageSize": 2
                              },
                              headers=self._get_auth_header())
        if not r.ok:
            raise PageConnectionError(
                f"get_page_exam中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()["result"]
            for exam_data in json_data["examList"]:
                exam = Exam(
                    id=exam_data["examId"],
                    name=exam_data["examName"]
                )
                exam.create_time = exam_data["examCreateDateTime"]
                exams.append(exam)
            hasNextPage: bool = json_data["hasNextPage"]
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"get_page_exam中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return exams, hasNextPage

    def get_latest_exam(self) -> ExamInfo:
        """获取最新考试"""
        self.update_login_status()
        r = self._session.get(Url.GET_RECENT_EXAM_URL,
                              headers=self._get_auth_header())
        if not r.ok:
            raise PageConnectionError(
                f"get_latest_exam中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()["result"]
            exam_info_data = json_data["examInfo"]

            subjects: ExtendedList[Subject] = ExtendedList()

            for subject_data in exam_info_data["subjectScores"]:
                subjects.append(Subject(
                    id=subject_data["topicSetId"],
                    name=subject_data["subjectName"],
                    code=subject_data["subjectCode"]
                ))

            exam_info = ExamInfo(
                id=exam_info_data["examId"],
                name=exam_info_data["examName"],
                subjects=subjects,
                classId=exam_info_data["classId"],
                grade_code=json_data["gradeCode"],
                is_final=exam_info_data["isFinal"]
            )
            exam_info.create_time = exam_info_data["examCreateDateTime"]
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"get_latest_exam中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return exam_info

    def get_exams(self) -> ExtendedList[Exam]:
        """获取所有考试"""
        exams: ExtendedList[Exam] = ExtendedList()
        i = 1
        check = True
        while check:
            cur_exams, check = self.get_page_exam(i)
            exams.extend(cur_exams)
            i += 1
        return exams

    def __get_self_mark(self, exam: Exam, has_total_score: bool) -> Mark:
        self.update_login_status()
        mark = Mark(exam=exam, person=self)
        r = self._session.get(Url.GET_MARK_URL,
                              params={"examId": exam.id},
                              headers=self._get_auth_header())
        if not r.ok:
            raise PageConnectionError(
                f"__get_self_mark中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()
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
                        exam_id=exam.id),
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
                        exam_id=exam.id,
                    ),
                    person=StuPerson(),
                    class_rank=exam.class_rank,
                    grade_rank=exam.grade_rank
                )
                # subject_score.create_time = 0
                mark.append(subject_score)
            self._set_exam_rank(mark)
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"__get_self_mark中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return mark

    def get_self_mark(self,
                      exam_data: Union[Exam, str] = "",
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
        self.update_login_status()
        subjects: ExtendedList[Subject] = ExtendedList()
        t = time.perf_counter()
        r = self._session.get(Url.GET_SUBJECT_URL,
                              params={"examId": exam.id},
                              headers=self._get_auth_header())
        print(time.perf_counter() - t)
        if not r.ok:
            raise PageConnectionError(
                f"__get_subjects中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()
            for subject in json_data["result"]["paperList"]:
                subjects.append(
                    Subject(id=subject["paperId"],
                            name=subject["subjectName"],
                            code=subject["subjectCode"],
                            standard_score=subject["standardScore"],
                            exam_id=exam.id))
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"__get_subjects中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return subjects

    def get_subjects(self, exam_data: Union[Exam, str] = "") -> ExtendedList[Subject]:
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
        self.update_login_status()
        subjects = self.get_subjects(exam)
        if _check_is_uuid(subject_data):  # 判断为id还是名称
            subject = subjects.find_by_id(subject_data)  # 为id
        else:
            subject = subjects.find_by_name(subject_data)  # 为名称
        return subject

    def get_subject(self,
                    subject_data: Union[Subject, str],
                    exam_data: Union[Exam, str] = "") -> Subject:
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
        subject = self.__get_subject(exam, subject_data)
        return subject if subject is not None else Subject()

    def __get_original(self, subject_id: str, exam_id: str) -> List[str]:
        self.update_login_status()
        r = self._session.get(Url.GET_ORIGINAL_URL,
                              params={
                                  "examId": exam_id,
                                  "paperId": subject_id,
                              },
                              headers=self._get_auth_header())
        if not r.ok:
            raise PageConnectionError(
                f"__get_original中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()
            if json_data["result"] == "":
                raise GetOriginalError(json_data["errorCode"], json_data["errorInfo"])
            image_urls = []
            for image_url in json.loads(json_data["result"]["sheetImages"]):
                image_urls.append(image_url)
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"__get_original中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return image_urls

    def get_original(self,
                     subject_data: Union[Subject, str],
                     exam_data: Union[Exam, str] = "") -> List[str]:
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
        subject = self.get_subject(subject_data, exam)
        if not subject:
            return []
        return self.__get_original(subject.id, exam.id)

    def get_clazzs(self) -> ExtendedList[StuClass]:
        """获取当前年级所有班级"""
        clazzs: ExtendedList[StuClass] = ExtendedList()
        r = self._session.get(Url.GET_CLAZZS_URL,
                              params={"d": int(time.time())})
        if not r.ok:
            raise PageConnectionError(f"get_clazzs中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()
            for clazz in json_data["clazzs"]:
                clazzs.append(
                    StuClass(name=clazz["name"],
                             id=clazz["id"],
                             grade=self.clazz.grade,
                             school=self.clazz.school))
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"get_clazzs中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return clazzs

    def get_clazz(self, clazz_data: Union[StuClass, str] = "") -> StuClass:
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
        self.update_login_status()
        classmates = StuPersonList()
        r = self._session.get(Url.GET_CLASSMATES_URL,
                              params={
                                  "r": f"{self.id}student",
                                  "clazzId": clazz_id
                              })
        if not r.ok:
            raise PageConnectionError(
                f"__get_classmates中出错, 状态码为{r.status_code}")
        try:
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
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"__get_classmates中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return classmates

    def get_classmates(self, clazz_data: Union[StuClass, str] = "") -> ExtendedList[StuPerson]:
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
        self.update_login_status()
        friends = StuPersonList()
        r = self._session.get(Url.GET_FRIEND_URL,
                              params={"d": int(time.time())})
        if not r.ok:
            raise PageConnectionError(f"get_friends中出错, 状态码为{r.status_code}")
        try:
            json_data = r.json()
            for friend in json_data["friendList"]:
                friends.append(
                    StuPerson(name=friend["friendName"], id=friend["friendId"]))
        except (JSONDecodeError, KeyError) as e:
            raise PageInformationError(
                f"get_friends中网页内容发生改变, 错误为{e}, 内容为\n{r.text}")
        return friends

    def invite_friend(self, friend: Union[StuPerson, str]) -> FriendMsg:
        """邀请朋友

        Args:
            friend (Union[StuPerson, str]): 用户id 或 StuPerson的实例

        Returns:
            FriendMsg
        """
        self.update_login_status()
        user_id = friend
        if isinstance(friend, StuPerson):
            user_id = friend.id
        r = self._session.get(Url.INVITE_FRIEND_URL,
                              params={
                                  "d": int(time.time()),
                                  "friendId": user_id,
                                  "isTwoWay": "true"
                              })
        if not r.ok:
            raise PageConnectionError(f"invite_friend中出错, 状态码为{r.status_code}")
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
        self.update_login_status()
        user_id = friend
        if isinstance(friend, StuPerson):
            user_id = friend.id
        r = self._session.get(Url.DELETE_FRIEND_URL,
                              params={
                                  "d": int(time.time()),
                                  "friendId": user_id
                              })
        if not r.ok:
            raise PageConnectionError(f"remove_friend中出错, 状态码为{r.status_code}")
        return r.json()["result"] == "success"
    
    def get_homeworks(self, size: int = 20, is_complete: bool = False, subject_code: str = "-1", createTime: int = 0)  -> ExtendedList[StuHomework]:
        """获取指定数量的作业(暂时不支持获取所有作业)

        Args:
            size (int): 返回的数量
            is_complete (bool): True 表示取已完成的作业, False 表示取未完成的作业
            subject_code (code): "01" 表示取语文作业, "02"表示取数学作业, 以此类推
            createTime (int): 取创建时间在多久以前的作业, 0表示从最新取 (暂时用不到)
        Returns:
            ExtendedList[StuHomework]: 作业(不包含作业资源)
        """
        self.update_login_status()
        r = self._session.get(Url.GET_HOMEWORK_URL, params={
            "pageIndex": 2,
            "completeStatus": 1 if is_complete else 0,
            "pageSize": size, # 取几个
            "subjectCode": subject_code,
            "token": self._get_auth_header()["XToken"],
            "createTime": createTime # 创建时间在多久以前的 0 为从最新开始
        })
        homeworks: ExtendedList[StuHomework] = ExtendedList()
        data = r.json()["result"]
        for each in data["list"]:
            homeworks.append(StuHomework(
                id=each["hwId"],
                title=each["hwTitle"],
                type=HwType(
                    name=each["homeWorkTypeDTO"]["typeName"],
                    code=each["homeWorkTypeDTO"]["typeCode"],
                ),
                begin_time=each["beginTime"] / 1000,
                end_time=each["endTime"] / 1000,
                create_time=each["createTime"] / 1000,
                subject=BasicSubject(
                    name=each["subjectName"],
                    code=each["subjectCode"]
                ),
                is_allow_makeup=bool(each["isAllowMakeup"]),
                class_id=each["classId"],
                ansPubData=HwAnsPubData(
                    name=each["openAnswerDTO"]["answerPubName"],
                    code=each["openAnswerDTO"]["answerPubType"]
                ),
                stu_hwid=each["stuHwId"]
            ))
        return homeworks
    
    def get_homework_resources(self, hwid: str, hw_typecode: int) -> List[HwResource]:
        """获取指定作业的作业资源(例如题目文档)

        Args:
            hwid (str): 作业id
            hw_typecode (int): 作业类型代码
        Returns:
            List[HwResource]: 作业资源
        """
        self.update_login_status()
        if hw_typecode == 102:
            return []
        r = self._session.post(Url.GET_HOMEWORK_RESOURCE_URL, json={
            "base":{
                "appId": "WNLOIVE",
                "appVersion": "",
                "sysVersion": "v1001",
                "sysType": "web",
                "packageName": "com.iflytek.edu.hw",
                "udid": self.id,
                "expand": {}
            },
            "params": {"hwId":hwid}
        }, headers={
            "Authorization": self._get_auth_header()["XToken"],
        })
        data = r.json()["result"]
        resources = []
        for each in data["topicAttachments"]:
            resources.append(HwResource(
                name=each["name"],
                path=each["path"]
            ))
        return resources

    def _set_exam_rank(self, mark: Mark):
        r = self._session.get(Url.GET_EXAM_LEVEL_TREND_URL, params={
            "examId": mark.exam.id,
            "pageIndex": 1,
            "pageSize": 1
        }, headers=self._get_auth_header())
        data = r.json()
        if data["errorCode"] != 0:
            return
        num = data["result"]["list"][0]["dataList"][0]["statTotalNum"]

        r = self._session.get(Url.GET_SUBJECT_DIAGNOSIS, params={
            "examId": mark.exam.id
        }, headers=self._get_auth_header())
        data = r.json()
        if data["errorCode"] != 0:
            return
        for each in data["result"]["list"]:
            each_mark = mark.find(lambda t: t.subject.code == each["subjectCode"])
            if each_mark is not None:
                each_mark.class_rank = math.ceil(each["myRank"] / 100 * num)
    
    def get_errorbook(self, exam_id, subject_id: str) -> List[ErrorBookTopic]:
        r = self._session.get(Url.GET_ERRORBOOK_URL, params={
            "examId": exam_id,
            "paperId": subject_id
        }, headers=self._get_auth_header())
        data = r.json()
        if data["errorCode"] != 0: #  {'errorCode': 40217, 'errorInfo': '暂时未收集到试题信息,无法查看', 'result': ''}
            raise Exception(data)
        result = []
        for each in data["result"]["wrongTopicAnalysis"]["topicList"]:
            result.append(ErrorBookTopic(
                analysis_html=each["analysisHtml"],
                answer_html=each["answerHtml"],
                answer_type=each["answerType"],
                is_correct=each["beCorrect"],
                class_score_rate=each["classScoreRate"],
                content_html=each["contentHtml"],
                difficulty=each["difficultyValue"],
                dis_title_number=each["disTitleNumber"],
                image_answer=each.get("imageAnswer"),
                paper_id=each["paperId"],
                subject_name=each["paperName"],
                score=each["score"],
                standard_answer=each["standardAnswer"],
                standard_score=each["standardScore"],
                topic_analysis_img_url=each["topicAnalysisImgUrl"],
                subject_id=each["topicId"],
                topic_img_url=each["topicImgUrl"],
                topic_source_paper_name=each["topicSourcePaperName"]
            ))
        return result