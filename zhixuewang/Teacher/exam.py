from typing import *


def get_score(self, user_num, clazz_id, topicSetId):
    r = self._session.get("https://www.zhixue.com/exportpaper/class/getExportStudentInfo/", params={
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
    r = self._session.get(f"https://www.zhixue.com/exportpaper/class/getSubjectChoice/?examId={examId}")
    d = r.json()
    return d["result"]

def get_class_score(self, classId, topicSetId) -> List[Dict[str, float]]:
    r = self._session.get("https://www.zhixue.com/exportpaper/class/getExportStudentInfo/", params={
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

def get_mark(self, examId, classId):
    topicSets = self.get_topicSets(examId)
    