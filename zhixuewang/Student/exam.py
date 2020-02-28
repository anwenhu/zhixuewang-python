import hashlib
import time
import uuid
import json
from zhixuewang.models.examModel import Exam, SubjectScore, Subject, Mark
from zhixuewang.Student.models.urlModel import (
    XTOKEN_URL, GET_EXAM_URL, GET_MARK_URL, GET_SUBJECT_URL, GET_ORIGINAL_URL)
from typing import List, Tuple
from zhixuewang.models.basicModel import ExtendedList
from zhixuewang.models.personModel import Person

class ExtraExam:
    def __get_auth_header(self, tokens = [""]) -> dict:
        """
        获取header
        :param tokens:
        :return:
        """
        def md5_encode(msg: str) -> str:
            m = hashlib.md5()
            m.update(msg.encode(encoding="utf-8"))
            return m.hexdigest()
        auth_guid = str(uuid.uuid4())
        auth_time_stamp = str(int(time.time() * 1000))
        auth_token = md5_encode(
            auth_guid + auth_time_stamp + "iflytek!@#123student")
        token = tokens[0]
        if token:
            return {
                "authbizcode": "0001",
                "authguid": auth_guid,
                "authtimestamp": auth_time_stamp,
                "authtoken": auth_token,
                "XToken": token
            }
        r = self._session.get(XTOKEN_URL, headers={
            "authbizcode": "0001",
            "authguid": auth_guid,
            "authtimestamp": auth_time_stamp,
            "authtoken": auth_token
        })
        if r.json()["errorCode"] != 0:
            raise Exception(r.json()["errorInfo"])
        tokens[0] = r.json()["result"]
        return self.__get_auth_header()


    def get_exam(self, exam_data: Exam or str = None) -> Exam:
        """
        获取考试
        :param exam_data:
            可以为考试id或考试名称
            为空时返回最新考试
            为Exam实例时直接返回
        :return:
        """
        if not exam_data:
            return self.get_latest_exam()
        if type(exam_data) == Exam:
            return exam_data
        exams = self.get_exams()
        if len(exam_data) < 36:
            exam = exams.find_by_name(exam_data)  # 为名称
        elif len(exam_data) == exam_data[14] == "4" and exam_data[8] == exam_data[13] == exam_data[18] == exam_data[23] == "-": # 判断为id还是名称
            exam = exams.find_by_id(exam_data)  # 为id
        else:
            exam = exams.find_by_name(exam_data)  # 为名称
        return exam


    def __get_page_exam(self, page: int) -> List[Exam]:
        """
        获取指定页数的考试列表
        :param page: 页数
        :return:
        """
        exams = ExtendedList()
        r = self._session.get(GET_EXAM_URL, params={
            "actualPosition": 0,
            "pageIndex": page,
            "pageSize": 10
        })
        json_data = r.json()
        for exam in json_data["examList"]:
            exams.append(Exam(
                id=exam["examId"],
                name=exam["examName"],
                create_time=int(exam["examCreateDateTime"]),
                exam_time=int(exam["examDateTime"]),
                # complete_time=
                grade_code=exam["gradeCode"],
                subject_codes=exam["subjectCodes"]
            ))
        return exams


    def get_latest_exam(self) -> Exam:
        """
        获取最新考试
        :return:
        """
        exams = self.__get_page_exam(1)
        if len(exams) == 0:
            return None
        return exams[0]


    def get_exams(self) -> List[Exam]:
        """
        获取所有考试
        :return:
        """
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
        mark = Mark(exam=exam)
        r = self._session.get(GET_MARK_URL,params={
            "examId": exam.id
        }, headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        json_data = json_data["result"]
        # exam.name = json_data["total_score"]["examName"]
        # exam.id = json_data["total_score"]["examId"]
        for subject in json_data["paperList"]:
            mark.append(SubjectScore(
                score=subject["userScore"],
                subject=Subject(
                    id=subject["paperId"],
                    name=subject["subjectName"],
                    code=subject["subjectCode"],
                    standard_score=subject["standardScore"],
                    exam=exam
                ),
                person=self,
                create_time=0
            ))
        if has_total_score:
            total_score = json_data["totalScore"]
            mark.append(SubjectScore(
                score=total_score["userScore"],
                subject=Subject(
                    id="",
                    name=total_score["subjectName"],
                    code="99",
                    standard_score=total_score["standardScore"],
                    exam=exam
                ),
                person=self,
                create_time=0
            ))
        return mark

    def get_self_mark(self, exam_data: Exam or str = None, has_total_score: bool = True) -> Mark:
        """
        获取指定考试的成绩
        :param exam_data: 
            可以为考试id或考试名称
            为空取最新考试
        :param has_total_score:
            是否计算总分,默认计算
        :return:
        """
        exam = self.get_exam(exam_data)
        if exam is None:
            return None
        return self.__get_self_mark(exam, has_total_score)
    
    def __get_subjects(self, exam: Exam) -> List[Subject]:
        subjects = ExtendedList()
        r = self._session.get(GET_SUBJECT_URL, params={
            "examId": exam.id
        }, headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        for subject in json_data["result"]["paperList"]:
            subjects.append(Subject(
                id=subject["paperId"],
                name=subject["subjectName"],
                code=subject["subjectCode"],
                standard_score=subject["standardScore"],
                exam=exam
            ))
        return subjects


    def get_subjects(self, exam_data: Exam or str = None) -> List[Subject]:
        """
        获得指定考试的所有学科(不算总分)
        :param exam_data: 
            可以为考试id或考试名称
            为空取最新考试
        :return:
        """
        exam = self.get_exam(exam_data)
        if exam is None:
            return None
        return self.__get_subjects(exam)

    def __get_subject(self, exam: Exam, subject_data: str):
        subjects = self.get_subjects()
        if subject_data.isdigit(): # 判断为id还是名称
            subject = subjects.find_by_id(subject_data)  # 为id
        else:
            subject = subjects.find_by_name(subject_data)  # 为名称
        return subject
    
    def get_subject(self, subject_data: str, exam_data: str = "") -> Subject:
        """
        获取学科
        :param exam_data:
            可以为考试id或考试名称
            为空时返回最新考试
        :param subject_data:
            可以为学科id或学科名称
        :return:
        """
        exam = self.get_exam(exam_data)
        if exam is None:
            return None
        return self.__get_subject(exam, subject_data)

    def __get_original(self, subject_id: str, exam_id: str) -> List[str]:
        r = self._session.get(GET_ORIGINAL_URL,params={
            "examId": exam_id,
            "paperId": subject_id,
        }, headers=self.__get_auth_header())
        json_data = r.json()
        if json_data["errorCode"] != 0:
            raise Exception(json_data["errorInfo"])
        image_urls = list()
        for image_url in json.loads(json_data["result"]["sheetImages"]):
            image_urls.append(image_url)
        return image_urls

    def get_original(self, subject_data: Subject or str, exam_data: Exam or str = None) -> list:
        """
        获得指定考试某一学科的原卷地址
        :param exam_data: 
            可以为考试id或考试名称
            为空取最新考试
            为Exam实例时直接返回
        :param subject_data: 
            可以为学科id或学科名称
        :return:
        """
        exam = self.get_exam(exam_data)
        if not exam:
            return None
        subject = self.get_subject(subject_data)
        if not subject:
            return None
        return self.__get_original(exam.id, subject.id)
       


    # def get_one_original_url(self, subject_name: str, exam: examModel = None, user_id: str = ""):
    #     if exam is None:
    #         exam = self.get_latest_exam()
    #     paper_id = self.__get_paper_id(exam.id, subject_name)
    #     if not paper_id:
    #         return ""
    #     return f"https://www.zhixue.com/classreport/class/student/checksheet/?userId={user_id}&paperId={paper_id}"
