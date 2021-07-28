from zhixuewang.models import StuClass
from zhixuewang.models import ExtendedList
from typing import List, Dict, Union
from zhixuewang.models import Person, Sex, Subject, SubjectScore
from zhixuewang.teacher.urls import Url
from zhixuewang.teacher.models import TeaPerson


class TeacherAccount(TeaPerson):
    """老师账号"""

    def __init__(self, session):
        super().__init__()
        self._session = session

    def set_base_info(self):
        r = self._session.get(
            Url.TEST_URL,
            headers={
                "referer":
                "https://www.zhixue.com/container/container/teacher/index/"
            })
        json_data = r.json()["teacher"]
        self.email = json_data.get("email")
        self.gender = Sex.BOY if json_data["gender"] == "1" else Sex.GIRL
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.name = json_data.get("name")
        self.roles = json_data["roles"]
        return self

    def get_score(self, user_num, clazz_id, topicSetId):
        r = self._session.get(
            "https://www.zhixue.com/exportpaper/class/getExportStudentInfo/",
            params={
                "type": "allTopicUserNum",
                "classId": clazz_id,
                "studentNum": user_num,
                "topicSetId": topicSetId,
                "topicNumber": "0",
                "startScore": "0",
                "endScore": "0",
            })
        d = r.json()
        return d.get("result")[0]["userScore"]

    def get_topicSets(self, examId):
        r = self._session.get(
            f"https://www.zhixue.com/exportpaper/class/getSubjectChoice/?examId={examId}"
        )
        d = r.json()
        return d["result"]

    def __get_class_score(self, classId: str, subjectId: str) -> List[SubjectScore]:
        r = self._session.get(
            Url.GET_REPORT_URL,
            params={
                "type": "export_single_paper_zip",
                "classId": classId,
                "studentNum": "",
                "topicSetId": subjectId,
                "topicNumber": "0",
                "startScore": "0",
                "endScore": "10000",
            })
        data = r.json()
        subjectScores = ExtendedList()
        for pair in data["result"]:
            subjectScores.append(SubjectScore(
                score=pair["userScore"],
                person=Person(name=pair["userName"]),
                subject=Subject(id=subjectId)
            ))
        return subjectScores
    
    def get_class_score(self, classData: Union[StuClass, str], subjectData: Union[Subject, str]):
        classId = classData.id if isinstance(classData, StuClass) else classData
        subjectId = subjectData.id if isinstance(subjectData, Subject) else subjectData
        return self.__get_class_score(classId, subjectId)