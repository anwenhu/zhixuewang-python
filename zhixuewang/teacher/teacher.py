import asyncio
from datetime import datetime
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
    Grade,
    TextBook,
    StuPerson,
)
from zhixuewang.teacher.models import (
    MarkingProgress,
    PageExam,
    TeaPerson,
    AcademicInfo
)
from zhixuewang.teacher.urls import Url


class TeacherAccount(Account, TeaPerson):
    """老师账号"""

    #! Advanced Information
    currentTeachClasses: list = []
    """当前教授的班级"""
    inProvince: str = None
    """教师所在的省份"""
    inCity: str = None
    """教师所在的城市"""
    currentSubject: Subject = None
    """当前教授的学科"""
    currentTeachingGrade: Grade = None
    """当前教授的年级"""
    currentTeachingTextbook: TextBook = None
    """当前使用的教科书"""
    currentSchool: School = None
    """当前的学校"""

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

        advanced_info = self._session.get(
            Url.GET_ADVANCED_INFORMATION_URL,
            headers={
                "referer": "https://www.zhixue.com/paperfresh/dist/assets/expertPaper.html"
            },
        )
        adv_result = advanced_info.json()["result"]
        self.inProvince = adv_result["province"]["name"]
        self.inCity = adv_result["city"]["name"]

        if type(adv_result["school"]) == None \
            or type(adv_result["curSubject"]) == None \
            or type(adv_result["grade"]) == None \
            or type(adv_result["textBookVersion"]) == None:
            raise TypeError(f"教师高级信息传回空值，原始JSON数据为\n School: {adv_result['school']}\n curSubject: {adv_result['curSubject']}\n grade: {adv_result['grade']} \n textBook: {adv_result['textBookVersion']}")
        
        self.currentSchool = School(
            name=adv_result["school"]["name"], id=adv_result["school"]["id"]
        )
        self.currentSubject = Subject(
            adv_result["curSubject"]["name"], code=adv_result["curSubject"]["code"]
        )
        self.currentTeachingGrade = Grade(
            adv_result["grade"]["name"], code=adv_result["grade"]["code"]
        )
        self.currentTeachingTextbook = TextBook(
            code=adv_result["textBookVersion"]["code"],
            name=adv_result["textBookVersion"]["name"],
            version=adv_result["bookVersion"]["name"],
            versionCode=adv_result["bookVersion"]["code"],
            #!TODO 暂无法通过对应的Code获取学科，暂时使用教师绑定的学科
            bindSubject=self.currentSubject,
        )
        teacGrade: Grade = None
        for i in adv_result["curTeachingGrades"]:
            teacGrade = Grade(name=i["name"], code=i["code"])
            for j in i["clazzs"]:
                #!TODO 暂无法获取班级所在学校，暂时使用教师绑定的学校
                self.currentTeachClasses.append(
                    StuClass(
                        id=j["code"],
                        name=j["name"],
                        grade=teacGrade,
                        school=self.currentSchool,
                    )
                )
            # 清空grade缓存
            teacGrade = None
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

    def get_student_status(
        self, clazzId: str, subjectCode: int, gradeCode: int, roleType: str = "teacher"
    ):
        """获取学生信息（如进步，退步等），返回临近生，下滑生，波动生"""
        self.update_login_status()
        r = self._session.get(
            Url.GET_STUDENT_STATUS_URL,
            headers={"referers": "https://www.zhixue.com/api-teacher/home/index"},
            params={
                "roleType": roleType,
                "gradeCode": str(gradeCode),
                "classId": clazzId,
                "subjectCode": str(subjectCode),
            },
        )
        data = r.json()["result"]
        critical_student: list = []  # 临近生
        backword_student: list = []  # 下滑
        unstable_student: list = []  # 波动
        if data["criticalStudents"] != None:
            for i in data["criticalStudents"]:
                critical_student.append(StuPerson(id=i["userId"], name=i["userName"]))
        if data["backwordStudents"] != None:
            for i in data["backwordStudents"]:
                backword_student.append(StuPerson(id=i["userId"], name=i["userName"]))
        if data["unstableStudents"] != None:
            for i in data["unstableStudents"]:
                unstable_student.append(StuPerson(id=i["userId"], name=i["userName"]))
        return (critical_student, backword_student, unstable_student)

    def get_school_exam_classes(
        self, school_id: str, subject_id: str
    ) -> List[StuClass]:
        self.update_login_status()
        return asyncio.run(self.__get_school_exam_classes(school_id, subject_id))

    def get_original_paper(
        self, user_id: str, paper_id: str, save_to_path: str
    ) -> bool:
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

    def get_teacher_roleText(self) -> list:
        """
        获得教师的角色文本
        Return:
            list: 教师的所有角色名称
        Raises:
            ValueError: 未知的角色
        """
        str_roles = []
        for role in self.roles:
            if role == "teacher":
                str_roles.append("教师")
            elif role == "subjectLeader":
                str_roles.append("备课组长")
            elif role == "gradeDirecter":
                str_roles.append("年级组长")
            elif role == "headteacher":
                str_roles.append("班主任")
            elif role == "headmaster":
                str_roles.append("校长")
            elif role == "schoolAdministrator":
                str_roles.append("校管理员")
            else:
                raise ValueError(f"教师角色{role}未知。已忽略。")

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
            headers={"token": self.get_token()},
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

    def get_academic_info(self) -> AcademicInfo:
        r = self._session.get(
            Url.GET_ACADEMIC_INFO_URL
        )
        data = r.json()["result"]
        

    def get_exams(
        self,
        class_id: str = "all",
        start_time: datetime = datetime(2020, 1, 1),
        end_time: datetime = datetime.now(),
        page_size: int = 15,
        page_index: int = 1,
    ) -> PageExam:
        """
        获取考试
        Args:
            class_id (str): 指定查看考试的班级, 默认为全部班级
            start_time (datetime): 指定查看考试的开始时间, 默认为2020年1月1日
            end_time (datetime): 指定查看考试的结束时间, 默认为现在
            page_size (int): 指定一页考试数
            page_index (int): 指定页数
        Return:
            PageExam: 考试信息和页数信息
        """
        r = self._session.get(
            Url.GET_EXAMS_URL,
            params={
                "examName": "",
                "gradeCode": "all",
                "classId": class_id,
                "subjectCode": "all",
                "searchType": "schoolYearType",
                "circlesYear": "",
                "examTypeCode": "all",
                "termId": "3feef3b1-a921-450e-a007-2e1d0bef7ba1",
                "teachingCycleId": "150ae8ea-a5ec-439b-957b-f27205f672b4",
                "startTime": int(start_time.timestamp() * 1000),
                "endTime": int(end_time.timestamp() * 1000),
                "pageSize": page_size,
                "pageIndex": page_index,
            },
        )
        exams = []
        data = r.json()["result"]
        if "classPaperSummaryList" not in data:
            return PageExam([], page_index, page_size, 0, False)
        for each in data["classPaperSummaryList"]:
            exams.append(
                Exam(
                    id=each["data"]["examId"],
                    name=each["data"]["examName"],
                    grade_code=each["data"]["gradeCode"],
                    subjects=ExtendedList(
                        [
                            Subject(name=one["name"])
                            for one in each["zxSubjects"]
                            if not one["isMultiSubject"]  # 排除复合学科如理综
                        ]
                    ),
                    create_time=each["data"]["createDateTime"] / 1000,
                    is_final=each["data"]["isFinal"]
                )
            )
        return PageExam(
            exams=exams,
            page_index=page_index,
            page_size=page_size,
            all_pages=data["pageInfo"]["allPages"][-1],
            has_next_page=page_index < data["pageInfo"]["allPages"][-1],
        )

    def get_token(self) -> str:
        if self._token is not None:
            return self._token
        r = self._session.get("https://www.zhixue.com/container/app/token/getToken")
        self._token = r.json()["result"]
        return self._token
