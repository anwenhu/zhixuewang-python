import hashlib
import random
import time
from json import loads
from ..models.examModel import *
from .models.urlModel import (
    XTOKEN_URL, GET_EXAM_URL, GET_MARK_URL, GET_PAPERID_URL, GET_ORIGINAL_URL)
from ..models.userModel import User


def __get_auth_header(self, XToken: str = None) -> dict:
    def md5_encode(msg: str) -> str:
        m = hashlib.md5()
        m.update(msg.encode(encoding="utf-8"))
        return m.hexdigest()

    def get_authguid() -> str:
        strChars = ["0", "1", "2", "3", "4", "5", "6",
                    "7", "8", "9", "a", "b", "c", "d", "e", "f"]
        t = [""] * 36
        for e in range(36):
            t[e] = random.choice(strChars)
        t[14] = "4"
        if t[19].isdigit():
            t[19] = "0123456789abcdef"[3 & int(t[19]) | 8]
        else:
            t[19] = "8"
        t[8] = t[13] = t[18] = t[23] = "-"
        return "".join(t)

    auth_guid = get_authguid()
    auth_time_stamp = str(int(time.time() * 1000))
    auth_token = md5_encode(
        auth_guid + auth_time_stamp + "iflytek!@#123student")
    if XToken:
        return {
            "authbizcode": "0001",
            "authguid": auth_guid,
            "authtimestamp": auth_time_stamp,
            "authtoken": auth_token,
            "XToken": XToken
        }
    r = self._session.get(XTOKEN_URL, headers={
        "authbizcode": "0001",
        "authguid": auth_guid,
        "authtimestamp": auth_time_stamp,
        "authtoken": auth_token
    })
    if r.json()["errorCode"] != 0:
        raise Exception(r.json()["errorInfo"])
    XToken = r.json()["result"]
    self._xtoken = XToken
    return self.__get_auth_header(XToken)


def get_exam_id(self, exam_name: str = None) -> str:
    """
    把考试名字转换为考试id
    :param exam_name:
        当name本身就是id，直接返回它本身
        name为空则返回最新考试id
    :return:
    """
    if exam_name is None:
        return self.get_latest_exam().examId
    exams = self.get_exams()
    for exam in exams:
        if exam_name == exam.examName:
            return exam.examId
    return ""


def __get_page_exam_data(self, page):
    r = self._session.get(
        GET_EXAM_URL,
        params={
            "actualPosition": 0,
            "pageIndex": page,
            "pageSize": 10
        }
    )
    json_data = r.json()
    return (json_data["examList"], True) if json_data.pop("hasNextPage") else (json_data["examList"], False)


def get_latest_exam(self) -> examModel:
    """
    获取最后一次考试信息
    :return:
    """
    exam = self.__get_page_exam_data(1)[0][0]
    return examModel(
        id=exam["examId"],
        name=exam["examName"]
    )


def get_exams(self) -> list:
    """
    获取所有考试信息
    :return:
    """
    exams = list()
    i = 1
    check = True
    while check:
        json_data, check = self.__get_page_exam_data(i)
        for exam in json_data:
            exams.append(examModel(
                id=exam["examId"],
                name=exam["examName"],
            ))
        i += 1

    return exams


def get_self_mark(self, exam: examModel = None) -> list:
    """
    获取成绩
    :param exam: 为空取最新考试
    :return:
    """
    mark = examMarkModel(list())
    if exam is None:
        exam = self.get_latest_exam()
    data = self._session.get(
        GET_MARK_URL,
        params={
            "examId": exam.id,
            "random": random.random()
        }
    ).json()["singleData"]
    u = len(data)
    for i in range(u):
        mark.append(subjectMarkModel(
            score=data[i]["score"],
            classRank=classMarkModel(
                avgScore=float(data[i]["classRank"]["avgScore"]),
                highScore=float(data[i]["classRank"]["highScore"]),
                lowScore=float(data[i]["classRank"]["lowScore"]),
                rank=int(data[i]["classRank"]["rank"])
            ),
            gradeRank=gradeMarkModel(
                avgScore=float(data[i]["gradeRank"]["avgScore"]),
                highScore=float(data[i]["gradeRank"]["highScore"]),
                lowScore=float(data[i]["gradeRank"]["lowScore"]),
            ),
            subjectName=data[i]["subjectName"],
            standardScore=data[i]["standardScore"],
            exam=exam
        ))
    return mark


def get_mark_with_weight(self, f: 'def(subjectName: str, score: int) -> int', exam: examModel = None) -> float:
    """
    根据用户自定义函数返回成绩
    :param f: 自定义函数
    :param exam: 为空取最新考试
    :return
    """
    mark = self.get_self_mark(exam)
    res_score = 0
    for subject in mark:
        res_score += f(subject.subjectName, subject.score)
    return res_score


"""
def getGrade(self, examdata, name):
    examId = self.id_name(examdata, "exam")
    userId = self.getStudentId(name)
    self._setUserPkcount(examId)
    if not userId:
        return "你输入的名字不存在"
    json = {
        "examId": examId,
        "random": random.random(),
        "pkId": userId
    }
    r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/personal/studentPkData/", params=json,
                            data=json, json=json)
    return r.json()[1]
"""


def __get_paper_id(self, exam_id: str, subject_name: str) -> str:
    """
    获得指定考试id和学科的paperid
    :param subject_name: 学科名称
    :param exam_id: 考试id
    :return:
        """
    r = self._session.get(GET_PAPERID_URL, params={"examId": exam_id},
                          headers=self.__get_auth_header(self._xtoken))
    json_data = r.json()
    if json_data["errorCode"] != 0:
        raise Exception(json_data["errorInfo"])
    for paper in json_data["result"]["paperList"]:
        if paper["subjectName"] == subject_name:
            return paper["paperId"]
    return ""


def get_original(self, subject_name: str, exam: examModel = None) -> list:
    """
    获得指定考试id或名称和学科的原卷地址
    :param subject_name: 学科
    :param exam: 为空取最新考试
    :return:
    """
    if exam is None:
        exam = self.get_latest_exam()
    paper_id = self.__get_paper_id(exam.id, subject_name)
    if not paper_id:
        return list()
    r = self._session.get(
        GET_ORIGINAL_URL,
        params={
            "examId": exam.id,
            "paperId": paper_id,
            "": ""
        },
        headers=self.__get_auth_header())
    json_data = r.json()
    if json_data["errorCode"] != 0:
        raise Exception(json_data["errorInfo"])
    image_urls = list()
    for image_url in loads(json_data["result"]["sheetImages"]):
        image_urls.append(image_url)
    return image_urls
