import re
import random
from json import loads

from .models import *


class Exam:
    def __init__(self, __session):
        self.__session = __session

    def get_exam_id(self, exam_name: str = None) -> str:
        """
        把考试名字转换为考试id
        :param exam_name:
            当name本身就是id，直接返回它本身
            name为空则返回最新考试id
        :return:
        """
        if exam_name and "-" in exam_name:
            return exam_name
        exams = self.get_exams()
        if exam_name is None:
            return exams[0].examId
        for exam in exams:
            if exam_name == exam.examName:
                return exam.examId
        else:
            return ""

    def get_exams(self):
        """
        获取所有考试信息
        :return:
        """
        exams = []

        def get_page_exam_names(page: str) -> bool:
            r = self.__session.get(
                "http://www.zhixue.com/zhixuebao/zhixuebao/main/getUserExamList/",
                params={
                    "actualPosition": 0,
                    "pageIndex": page,
                    "pageSize": 10,
                }
            )
            json_data = r.json()
            for exam in json_data["examList"]:
                exams.append(examDataModel(
                    examId=exam["examId"],
                    examName=exam["examName"],
                ))
            return json_data["hasNextPage"]

        i = 1
        while True:
            if not get_page_exam_names(i):
                break
            i += 1
        return exams

    def get_self_grade(self, data: str = None) -> list:
        """
        获取成绩
        :param data:
            考试id或名称,为空则取最新考试id
        :return:
        """
        grades = list()
        exam_id = self.get_exam_id(data)
        data = self.__session.get(
            "http://www.zhixue.com/zhixuebao/zhixuebao/feesReport/getStuSingleReportDataForPK/",
            params={
                "examId": exam_id,
                "random": random.random()
            }
        ).json()["singleData"]

        u = len(data)
        for i in range(u):
            grades.append(subjectDataModel(**{
                "score": data[i]["score"],
                "classRank": classDataModel(**{
                    "avgScore": data[i]["classRank"]["avgScore"],
                    "highScore": data[i]["classRank"]["highScore"],
                    "lowScore": data[i]["classRank"]["lowScore"],
                    "rank": data[i]["classRank"]["rank"]
                }),
                "gradeRank": gradeDataModel(**{
                    "avgScore": data[i]["gradeRank"]["avgScore"],
                    "highScore": data[i]["gradeRank"]["highScore"],
                    "lowScore": data[i]["gradeRank"]["lowScore"],
                }),
                "subjectName": data[i]["subjectName"],
                "standardScore": data[i]["standardScore"],
                "examName": data[i]["examName"],
                "examId": data[i]["examId"]
            }))
        return grades

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

    def __get_paper_id(self, exam_id: str, subject: str) -> str:
        """
        获得指定考试id和学科的paperid
        :param subject:学科
        :param exam_id:考试id
        :return:
         """
        paperid = False
        data = {
            "examId": exam_id,
            "isHomework": "false",
            "random": random.random()
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/getUserExamDataList/", params=data)
        json = r.json()
        r.close()
        for each in json["userExamDataList"]:
            if each["subjectName"] == subject:
                paperid = each["paperId"]
                break
        return paperid

    def get_original(self, subject: str, data: str = None) -> list:
        """
        获得指定考试id或名称和学科的原卷地址
        :param subject:学科
        :param data:考试id或名称
        :return:
        """
        exam_id = self.get_exam_id(data)
        paper_id = self.__get_paper_id(exam_id, subject)
        if not paper_id:
            return []
        data = {
            "paperId": paper_id,
            "examId": exam_id
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/checksheet/", params=data)
        imageurls = loads(re.findall(r"sheetImages = (\[.+?\])", r.text)[0])
        return imageurls
