def get_score(self, user_num: str, clazz_id: str, subject_id: str):
    r = self._session.get(
        "https://www.zhixue.com/exportpaper/class/getExportStudentInfo/",
        params={
            "type": "allTopicUserNum",
            "classId": clazz_id,
            "studentNum": user_num,
            "topicSetId": subject_id,
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


def get_class_subject_scores(self, class_id: str, subject_id: str) -> ClassSubjectScores:
    """获取指定班级的某科分数
    Args:
        class_id (str): 班级id
        subject_id (str): 科目id
    Returns:
        ClassSubjectScores
    """
    return ClassSubjectScores(asyncio.run(self.__get_class_score(class_id, subject_id)))

async def __get_class_scores(self, class_id: str, exam_id: str) -> ClassScores:
    """获取指定班级的某场考试的所有分数
    Args:
        class_id (str): 班级id
        exam_id (str): 考试id
    Returns:
        ExtendedList[SubjectScore]: 
    """
    subjects = self.get_exam_subjects(exam_id)
    tasks = []
    for subject in subjects:
        tasks.append(self.get_class_subject_scores(class_id, subject.id))
    result = await asyncio.gather(*tasks)
    return ClassScores(list(result))

def get_session_tgt(tgt: str):
    session = get_basic_session()
    session.cookies.set("CASTGC", tgt, domain="open.changyan.com")
    r = session.get(Url.SSO_URL)
    json_obj = json.loads(r.text.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1001:
        print(r.text)
        raise LoginError("tgt 已失效")
    r = session.post(Url.SERVICE_URL, data={
        "action": "login",
        "ticket": json_obj["data"]["st"],
    })
    return session