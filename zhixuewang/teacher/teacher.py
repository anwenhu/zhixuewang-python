import asyncio
from typing import List, Tuple
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
from zhixuewang.teacher.models import MarkingProgress, PageExam, TeaPerson, AcademicInfo
from zhixuewang.teacher.urls import Url


class TeacherAccount(Account, TeaPerson):
    """老师账号"""

    teaching_classes: list = []
    province: str = None
    city: str = None
    subject: Subject = None
    teaching_grade: Grade = None
    teaching_textbook: TextBook = None
    school: School = None

    def __init__(self, session):
        super().__init__(session, Role.teacher)
        self.roles = None
        self._token = None

    def set_advanced_info(self):
        r = self._session.get(
            Url.GET_ADVANCED_INFORMATION_URL,
            headers={
                "referer": "https://www.zhixue.com/paperfresh/dist/assets/expertPaper.html"
            },
        )
        if r.status_code != 200:
            return self
        data = r.json()["result"]
        self.province = data["province"]["name"]
        self.city = data["city"]["name"]
        if data["school"]:
            self.school = School(
                name=data["school"]["name"], id=data["school"]["id"]
            )
        if data["curSubject"]:
            self.subject = Subject(
                data["curSubject"]["name"], code=data["curSubject"]["code"]
            )
        if data["grade"]:
            self.teaching_grade = Grade(
                data["grade"]["name"], code=data["grade"]["code"]
            )
        if data["textBookVersion"]:
            self.teaching_textbook = TextBook(
                code=data["textBookVersion"]["code"],
                name=data["textBookVersion"]["name"],
                version=data["bookVersion"]["name"],
                versionCode=data["bookVersion"]["code"],
                #!TODO 暂无法通过对应的Code获取学科，暂时使用教师绑定的学科
                bindSubject=self.subject,
            )
        for teaching_grade in data["curTeachingGrades"]:
            for clazz in teaching_grade["clazzs"]:
                #!TODO 暂无法获取班级所在学校，暂时使用教师绑定的学校
                self.teaching_classes.append(
                    StuClass(
                        id=clazz["code"],
                        name=clazz["name"],
                        grade=Grade(
                            name=teaching_grade["name"], code=teaching_grade["code"]
                        ),
                        school=self.school,
                    )
                )
        return self

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

    def get_student_status(
        self,
        clazz_id: str,
        subject_code: str,
        grade_code: str,
        role_type: str = "teacher",
    ) -> Tuple[List[StuPerson], List[StuPerson], List[StuPerson]]:
        """获取学生信息（如进步，退步等），返回临近生，下滑生，波动生
        Args:
            clazz_id (str): 为需要查询班级id
            subject_code (str): 为需要查询的学科code
            grade_code (str): 科目code
            role_type (str)
        Return:
            Tuple[List[StuPerson], List[StuPerson], List[StuPerson]]: 由 临近生,下滑生,波动生 组成的元组
        """
        self.update_login_status()
        r = self._session.get(
            Url.GET_STUDENT_STATUS_URL,
            headers={"referers": "https://www.zhixue.com/api-teacher/home/index"},
            params={
                "roleType": role_type,
                "gradeCode": grade_code,
                "classId": clazz_id,
                "subjectCode": subject_code,
            },
        )
        data = r.json()["result"]
        critical_student: list = []  # 临近生
        backword_student: list = []  # 下滑生
        unstable_student: list = []  # 波动生
        if data["criticalStudents"] != None:
            critical_student = [
                StuPerson(id=i["userId"], name=i["userName"])
                for i in data["criticalStudents"]
            ]
        if data["backwordStudents"] != None:
            backword_student = [
                StuPerson(id=i["userId"], name=i["userName"])
                for i in data["backwordStudents"]
            ]
        if data["unstableStudents"] != None:
            unstable_student = [
                StuPerson(id=i["userId"], name=i["userName"])
                for i in data["unstableStudents"]
            ]
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

    def get_teacher_roleText(self) -> List[str]:
        """
        获得教师的角色文本
        Return:
            List[str]: 教师的所有角色名称(忽略未知的教师角色)
        """
        str_roles = []
        role_table = {
            "teacher": "教师",
            "subjectLeader": "备课组长",
            "gradeDirecter": "年级组长",
            "headteacher": "班主任",
            "headmaster": "校长",
            "schoolAdministrator": "校管理员",
        }
        for role in self.roles:
            str_role = role_table.get(role)
            if str_role is None:
                print(f"教师角色{role}未知。已忽略。")
            else:
                str_roles.append(str_role)
        return str_roles

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

    def _get_academic_info(self) -> List[AcademicInfo]:
        """
        获取学术信息用以获取教师考试
        """
        r = self._session.get(Url.GET_AcademicTermTeachingCycle_URL)
        data = r.json()["result"]
        result = []
        for did in data["termTeachingCycleMap"]:
            d = data["termTeachingCycleMap"][did][0]
            result.append(
                AcademicInfo(
                    teaching_cycle_id=d["id"],
                    circles_year=str(did),
                    term_id=d["termId"],
                    begin_time=d["beginTime"],
                    end_time=d["endTime"],  #! 这两个都使用Unix时间戳，单位ms
                    school_id=data["schoolId"],
                )
            )
        result = sorted(result, key=lambda _: _.begin_time, reverse=True)
        return result

    def get_exams(
        self,
        year: int = 0,
        index: int = 1,
        class_id: str = "all",
        exam_name: str = "",
        grade_code: str = "all",
        subject_code: str = "all",
        exam_type_code: str = "all",
        page_size: int = 15,
        page_index: int = 1,
    ) -> PageExam:
        """
        获取考试, 有学年和学期两种查询方式
        默认获取最新学期的考试
        `year`和`index`只需要传一个即可，均传默认使用`year`
        Args:
            year (int): 需要查询的年级，如2022级则传入2022
            index (int): 查询距离现在第几个学期, 如传入3表示获取上三个学期的考试
            class_id (str): 指定查看考试的班级, 默认为全部班级
            exam_name (str): 指定需要查看的考试名称
            grade_code (str): 指定查看考试的年级
            subject_code (str): 指定查看考试的学科类型
            exam_type_code (str): 指定查看考试的类型，默认为全部
            page_size (int): 指定一页考试数
            page_index (int): 指定页数
        Return:
            PageExam: 考试信息和页数信息
        """
        params_data = {
            "examName": exam_name,
            "gradeCode": grade_code,
            "classId": class_id,
            "subjectCode": subject_code,
            "examTypeCode": exam_type_code,
            "pageSize": page_size,
            "pageIndex": page_index,
        }
        if year == 0:
            #! 按 学期 查询
            academic_infos = self._get_academic_info()
            academic_info = academic_infos[index - 1]
            print(academic_info)
            params_data.update(
                {
                    "searchType": "schoolYearType",
                    "circlesYear": academic_info.circles_year,
                    "examTypeCode": exam_type_code,
                    "termId": academic_info.term_id,
                    "teachingCycleId": academic_info.teaching_cycle_id,
                    "startTime": academic_info.begin_time,
                    "endTime": academic_info.end_time,
                }
            )
            r = self._session.get(Url.GET_EXAMS_URL, params=params_data)
        else:
            # 按 学级 查询
            params_data.update(
                {
                    "searchType": "circlesType",
                    "circlesYear": year,
                    "termId": "",
                    "teachingCycleId": "",
                    "pageSize": page_size,
                    "pageIndex": page_index,
                }
            )
            r = self._session.get(Url.GET_EXAMS_URL, params=params_data)
        print(r.url)
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
                    is_final=each["data"]["isFinal"],
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

    def get_session(self):
        return self._session
