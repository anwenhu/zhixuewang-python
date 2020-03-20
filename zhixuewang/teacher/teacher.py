from typing import List, Dict
from zhixuewang.teacher.urls import Url
from zhixuewang.teacher.models import TeaPerson


class Teacher(TeaPerson):
    """老师账号"""
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.role = "teacher"

    def set_base_info(self):
        r = self._session.get(
            Url.TEST_URL,
            headers={
                "referer":
                "https://www.zhixue.com/container/container/teacher/index/"
            })
        json_data = r.json()["teacher"]
        self.email = json_data.get("email")
        self.gender = "男" if json_data["gender"] == "1" else "女"
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.name = json_data.get("name")
        self.role = json_data["roles"][-1]
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

    def get_class_score(self, classId, topicSetId) -> List[Dict[str, float]]:
        r = self._session.get(
            "https://www.zhixue.com/exportpaper/class/getExportStudentInfo/",
            params={
                "type": "export_single_paper_zip",
                "classId": classId,
                "studentNum": "",
                "topicSetId": topicSetId,
                "topicNumber": "0",
                "startScore": "0",
                "endScore": "10000",
            })
        d = r.json()
        return [{
            "name": i["userName"],
            "score": i["userScore"],
        } for i in d["result"]]


class Headmaster(Teacher):  # 校长
    def __init__(self, session):
        super().__init__(session)
        self.role = "headmaster"


class Headteacher(Teacher):  # 年级主任 / 班主任
    def __init__(self, session):
        super().__init__(session)
        self.role = "headteacher"
