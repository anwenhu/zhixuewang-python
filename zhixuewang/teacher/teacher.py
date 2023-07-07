import asyncio
from typing import List

import httpx
from zhixuewang.models import (
    Account,
    Exam,
    ExtendedList,
    Role,
    School,
    StuClass,
    Subject,
)
from zhixuewang.teacher.models import (
    MarkingProgress,
    TeaPerson,
)
from zhixuewang.teacher.urls import Url


class TeacherAccount(Account, TeaPerson):
    """老师账号"""

    def __init__(self, session):
        super().__init__(session, Role.teacher)
        self.roles = None
        self._token = None

    def set_base_info(self):
        r = self._session.get(
            Url.TEST_URL,
            headers={
                "referer": "https://www.zhixue.com/container/container/teacher/index/"
            },
        )
        json_data = r.json()["teacher"]
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.name = json_data.get("name")
        self.roles = json_data["roles"]
        return self

    async def __get_school_exam_classes(
            self, school_id: str, subject_id: str
    ) -> List[StuClass]:
        async with httpx.AsyncClient(cookies=self._session.cookies) as client:
            r = await client.get(
                Url.GET_EXAM_SCHOOLS_URL,
                params={"schoolId": school_id, "markingPaperId": subject_id},
            )
            data = r.json()
            if data is None:
                return []
            classes = []

            for each in data:
                classes.append(
                    StuClass(
                        id=each["classId"],
                        name=each["className"],
                        school=School(id=each["schoolId"]),
                    )
                )
            return classes

    def get_school_exam_classes(
            self, school_id: str, subject_id: str
    ) -> List[StuClass]:
        self.update_login_status()
        return asyncio.run(self.__get_school_exam_classes(school_id, subject_id))

    def get_original_paper(self, user_id: str, paper_id: str, save_to_path: str) -> bool:
        """
        获得原卷
        Args:
            user_id (str): 为需要查询原卷的userId
            paper_id (str): 为需要查询的学科ID(topicSetId)
            save_to_path (str): 为原卷保存位置(html文件), 精确到文件名
        Return:
            bool: 正常会返回True
        """
        data = self._session.get(
            Url.ORIGINAL_PAPER_URL, params={"userId": user_id, "paperId": paper_id}
        )
        with open(save_to_path, encoding="utf-8", mode="w+") as fhandle:
            fhandle.writelines(
                data.text.replace("//static.zhixue.com", "https://static.zhixue.com")
            )
        return True

    def get_exam_subjects(self, exam_id: str) -> ExtendedList[Subject]:
        """
        获取某个考试的考试科目
        Args:
            exam_id (str): 为需要查询考试的id
        Return:
            bool: 正常会返回True
        """
        self.update_login_status()
        r = self._session.get(Url.GET_EXAM_SUBJECTS_URL, params={"examId": exam_id})
        data = r.json()["result"]
        subjects = []
        for each in data:
            name = each["subjectName"]
            if name != "总分" and (not each.get("isSubjectGroup")):  # 排除学科组()
                subjects.append(
                    Subject(
                        id=each["topicSetId"],
                        name=each["subjectName"],
                        code=each["subjectCode"],
                        standard_score=each["standScore"],
                    )
                )
        return ExtendedList(sorted(subjects, key=lambda x: x.code, reverse=False))

    def get_exam_detail(self, exam_id: str) -> Exam:
        """
        获取某个考试的详细情况
        包括参考学校和考试科目
        Args:
            exam_id (str): 为需要查询考试的id
        Return:
            Exam
        """
        self.update_login_status()
        r = self._session.post(Url.GET_EXAM_DETAIL_URL, data={"examId": exam_id})
        data = r.json()["result"]
        exam = Exam()
        schools: ExtendedList[School] = ExtendedList()
        for each in data["schoolList"]:
            schools.append(School(id=each["schoolId"], name=each["schoolName"]))
        exam.id = exam_id
        exam.name = data["exam"]["examName"]
        exam.grade_code = data["exam"]["gradeCode"]

        exam.schools = schools
        exam.status = str(data["exam"]["isCrossExam"])
        exam.subjects = self.get_exam_subjects(exam_id)
        return exam

    def get_marking_progress(
            self,
            subject_id: str,
    ) -> List[MarkingProgress]:
        """
        获取某场考试指定科目阅卷情况
        Args:
            subject_id (str): 科目id
        Return:
            List[MarkingProgress]
        """
        r = self._session.post(
            "https://pt-ali-bj-re.zhixue.com/marking/marking/markingTopicProgress/",
            data={"markingPaperId": subject_id},
            headers={"token": self.get_token()}
        )
        data = r.json()
        result = []
        for each in data:
            result.append(
                MarkingProgress(
                    topic_number=each["topicNumber"],
                    complete_rate=each["comleteRate"],
                    complete_count=each["completeCount"],
                    all_count=each["allCount"],
                )
            )
        return result

    def get_token(self) -> str:
        if self._token is not None:
            return self._token
        r = self._session.get("https://www.zhixue.com/container/app/token/getToken")
        self._token = r.json()["result"]
        return self._token
