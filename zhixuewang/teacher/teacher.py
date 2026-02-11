import json
import re
from typing import List, Optional

from zhixuewang.models import (
    Account,
    BasicSubject,
    Exam,
    ExtendedList,
    Grade,
    Role,
    School,
    StuClass,
    Subject,
    TextBook,
)
from zhixuewang.teacher.models import (
    AcademicInfo,
    AnswerRecordDetail,
    MarkingProgress,
    OriginalPaper,
    PageExam,
    Phase,
    PhaseSubjectGrade,
    Region,
    SubTopicDetail,
    TeacherMarkingRecord,
    TeacherRole,
    TeaPerson,
)
from zhixuewang.teacher.urls import Url


class TeacherAccount(Account, TeaPerson):
    """老师账号"""

    teaching_classes: List[StuClass] = []
    """教学班级列表"""
    school: Optional[School] = None
    """所在学校"""
    cur_phase: Optional[Phase] = None
    """当前学段"""
    cur_subject: Optional[BasicSubject] = None
    """当前学科"""
    book_version: Optional[str] = None
    """书籍版本"""
    textbook_version: Optional[TextBook] = None
    """教科书版本"""
    phase_subjects_grades: List[PhaseSubjectGrade] = []
    """学段-学科-年级信息"""
    cur_teaching_grades: List[Grade] = []
    """当前教学年级"""

    def __init__(self, session):
        super().__init__(session, Role.teacher)
        self._token = None
    
    def to_teacher(self) -> "TeacherAccount":
        """将Account转换为TeacherAccount"""
        return self

    def set_advanced_info(self):
        """设置教师详细信息"""
        r = self._session.get(
            Url.GET_ADVANCED_INFORMATION_URL,
            headers={
                "referer": "https://www.zhixue.com/paperfresh/dist/assets/expertPaper.html"
            },
        )
        if r.status_code != 200:
            return self
        data = r.json()["result"]
        
        # 基本信息
        self.id = data.get("id", "")
        self.login_name = data.get("loginName", "")
        self.name = data.get("name", "")
        self.mobile = data.get("mobile", "")
        
        # 角色信息
        if "roles" in data:
            self.roles = []
            for role_data in data["roles"]:
                self.roles.append(TeacherRole.from_zxw(role_data["eName"]))
        
        # 地区信息
        if data.get("province"):
            self.province = Region(
                code=data["province"].get("code", ""),
                name=data["province"].get("name", ""),
                level=data["province"].get("level"),
                id=data["province"].get("id", "")
            )
        if data.get("city"):
            self.city = Region(
                code=data["city"].get("code", ""),
                name=data["city"].get("name", ""),
                level=data["city"].get("level"),
                id=data["city"].get("id", "")
            )
        if data.get("distinct"):
            self.district = Region(
                code=data["distinct"].get("code", ""),
                name=data["distinct"].get("name", ""),
                level=data["distinct"].get("level"),
                id=data["distinct"].get("id", "")
            )
        
        # 学校信息
        if data.get("school"):
            self.school = School(
                id=data["school"].get("id", ""),
                name=data["school"].get("name", "")
            )
        
        # 当前学段
        if data.get("curPhase"):
            self.cur_phase = Phase(
                code=data["curPhase"].get("code", ""),
                name=data["curPhase"].get("name", "")
            )
        
        # 当前学科
        if data.get("curSubject"):
            self.cur_subject = BasicSubject(
                code=data["curSubject"].get("code", ""),
                name=data["curSubject"].get("name", "")
            )
        
        # 书籍版本
        if data.get("bookVersion"):
            self.book_version = data["bookVersion"].get("name", "")
        
        # 教科书版本
        if data.get("textBookVersion") and self.cur_subject:
            self.textbook_version = TextBook(
                code=data["textBookVersion"].get("code", ""),
                name=data["textBookVersion"].get("name", ""),
                version=self.book_version or "",
                versionCode=data.get("bookVersion", {}).get("code", 0),
                bindSubject=self.cur_subject
            )
        
        # 当前教学年级
        if "curTeachingGrades" in data:
            self.cur_teaching_grades = []
            for grade_data in data["curTeachingGrades"]:
                grade = Grade(
                    code=grade_data.get("code"),
                    name=grade_data.get("name")
                )
                self.cur_teaching_grades.append(grade)
                
                # 提取教学班级
                if "clazzs" in grade_data:
                    for clazz_data in grade_data["clazzs"]:
                        self.teaching_classes.append(
                            StuClass(
                                id=clazz_data.get("code"),
                                name=clazz_data.get("name"),
                                grade=grade,
                                school=self.school or School()
                            )
                        )
        
        # 学段-学科-年级信息
        if "phaseAndSubjects" in data:
            self.phase_subjects_grades = []
            for psg_data in data["phaseAndSubjects"]:
                phase = Phase(
                    code=psg_data.get("phase", {}).get("code", ""),
                    name=psg_data.get("phase", {}).get("name", "")
                )
                subjects = [
                    BasicSubject(
                        code=s.get("code", ""),
                        name=s.get("name", "")
                    )
                    for s in psg_data.get("subjects", [])
                ]
                grades = [
                    Grade(
                        code=g.get("code", ""),
                        name=g.get("name", "")
                    )
                    for g in psg_data.get("grades", [])
                ]
                self.phase_subjects_grades.append(
                    PhaseSubjectGrade(
                        phase=phase,
                        subjects=subjects,
                        grades=grades
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
        # 解析角色，跳过未知角色
        self.roles = []
        for role in json_data.get("roles", []):
            try:
                self.roles.append(TeacherRole.from_zxw(role))
            except ValueError:
                # 跳过未知角色（如parent等）
                pass
        return self

    def get_school_exam_classes(
        self, school_id: Optional[str] = None, topic_set_id: Optional[str] = None, exam_id: Optional[str] = None
    ) -> ExtendedList[StuClass]:
        """获取某个学校参加某个考试的班级列表, 学校id默认为当前教师所在学校, 科目id和考试id两者必须传一个，若传入多个则优先使用科目id.
        tips: 班级信息只能获取到学校的id信息,无其余信息
        """
        if school_id is None:
            if self.school is None:
                raise ValueError("教师未关联学校, 无法获取学校ID")
            school_id = self.school.id
        if topic_set_id is None and exam_id is None:
            raise ValueError("必须传入科目id或考试id其中一个参数")
        if topic_set_id is None and exam_id is not None:
            subjects = self.get_exam_subjects(exam_id)
            if len(subjects) == 0:
                return ExtendedList()
            topic_set_id = subjects[0].id
        r = self._session.get(
            Url.GET_EXAM_SCHOOLS_URL,
            params={"schoolId": school_id, "markingPaperId": topic_set_id},
        )
        data = r.json()
        print(data)
        if data is None:
            return ExtendedList()
        classes: ExtendedList[StuClass] = ExtendedList()

        for each in data:
            classes.append(
                StuClass(
                    id=each["classId"],
                    name=each["className"],
                    grade=Grade(code=each["gradeCode"], name=each["gradeName"]),
                    school=School(id=each["schoolId"]),
                )
            )
        return classes

    
    def get_original_paper(
        self, user_id: str, topic_set_id: str, save_to_path: Optional[str] = None
    ) -> OriginalPaper:
        """获得原卷信息以及渲染后的HTML文件
        Args:
            user_id (str): 需要查询原卷的userId
            topic_set_id (str): 需要查询的学科ID(topicSetId)
            save_to_path (str, optional): 原卷保存位置(html文件), 精确到文件名。如果为None则不保存
        Returns:
            OriginalPaper: 解析后的原卷数据对象
        """
        r = self._session.get(
            Url.ORIGINAL_PAPER_URL, params={"userId": user_id, "paperId": topic_set_id}
        )
        html_content = r.text
        
        # 保存HTML文件（如果指定了路径）
        if save_to_path:
            with open(save_to_path, encoding="utf-8", mode="w+") as f:
                f.writelines(
                    html_content.replace("/api-classreport", "https://www.zhixue.com/api-classreport")
                )
        
        # 解析原卷数据
        return self._parse_original_paper_html(html_content, user_id, topic_set_id)
    
    def _parse_original_paper_html(self, html_content: str, user_id: str, topic_set_id: str) -> OriginalPaper:
        """解析原卷HTML内容
        Args:
            html_content (str): HTML内容
            user_id (str): 学生ID
            topic_set_id (str): 科目ID
        Returns:
            OriginalPaper: 解析后的原卷数据对象
        """
        # 提取JavaScript变量
        total_score = 0.0
        answer_details = []
        answer_sheet_images = []
        
        # 提取totalScore
        total_score_match = re.search(r'var totalScore = ([\d.]+);', html_content)
        if total_score_match:
            total_score = float(total_score_match.group(1))
        
        # 提取answerSheetImages
        sheet_images_match = re.search(r'var sheetImages = (\[.*?\]);', html_content, re.DOTALL)
        if sheet_images_match:
            try:
                sheet_images_str = sheet_images_match.group(1)
                answer_sheet_images = json.loads(sheet_images_str)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回空列表
                answer_sheet_images = []
        
        # 提取sheetDatas（包含userAnswerRecordDTO）
        sheet_datas_match = re.search(r'var sheetDatas = ({.*?});[\s\n]*var sheetImages', html_content, re.DOTALL)
        if sheet_datas_match:
            try:
                sheet_datas_str = sheet_datas_match.group(1)
                sheet_datas = json.loads(sheet_datas_str)
                
                # 解析用户答题记录
                user_answer_record = sheet_datas.get("userAnswerRecordDTO", {})
                
                
                # 解析答题详情
                for detail_data in user_answer_record.get("answerRecordDetails", []):
                    # 解析小题（主观题）
                    sub_topics = []
                    for sub_topic_data in detail_data.get("subTopics", []):
                        # 解析教师批改记录
                        marking_records = []
                        for marking_record_data in sub_topic_data.get("teacherMarkingRecords", []):
                            marking_records.append(TeacherMarkingRecord(
                                score=marking_record_data.get("score", 0.0),
                                marking_time=marking_record_data.get("markingTime", 0),
                                teacher_name=marking_record_data.get("teacherName", ""),
                                teacher_id=marking_record_data.get("teacherId", ""),
                                role=marking_record_data.get("role", ""),
                                is_excellent=marking_record_data.get("isExcellent", False),
                                is_typical_error=marking_record_data.get("isTypicalError", False),
                                marking_content=marking_record_data.get("markingContent", "")
                            ))
                        
                        sub_topics.append(SubTopicDetail(
                            score=sub_topic_data.get("score", 0.0),
                            sub_topic_index=sub_topic_data.get("subTopicIndex", -1),
                            score_source=sub_topic_data.get("scoreSource", ""),
                            teacher_marking_records=marking_records
                        ))
                    
                    answer_details.append(AnswerRecordDetail(
                        topic_number=detail_data.get("topicNumber", 0),
                        disp_title=detail_data.get("dispTitle", ""),
                        answer=detail_data.get("answer", ""),
                        score=detail_data.get("score", 0.0),
                        standard_score=detail_data.get("standardScore", 0.0),
                        is_correct=detail_data.get("isCorrect", False),
                        answer_type=detail_data.get("answerType", ""),
                        source_category_name=detail_data.get("sourceCategoryName", ""),
                        topic_type_id=detail_data.get("topicTypeId", ""),
                        sub_topics=sub_topics,
                        is_excellent=detail_data.get("isExcellent", False),
                        is_typical_error=detail_data.get("isTypicalError", False),
                        marking_paper_topic_id=detail_data.get("markingPaperTopicId", "")
                    ))
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回空数据
                pass
        
        return OriginalPaper(
            user_id=user_id,
            topic_set_id=topic_set_id,
            total_score=total_score,
            answer_details=answer_details,
            answer_sheet_images=answer_sheet_images
        )

    def get_exam_subjects(self, exam_id: str) -> ExtendedList[Subject]:
        """获取某个考试的总考试科目"""
        r = self._session.get(Url.GET_EXAM_SUBJECTS_URL, params={"examId": exam_id})
        data = r.json()["result"]
        subjects: ExtendedList[Subject] = ExtendedList()
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
        subjects.sort(key=lambda x: x.code, reverse=False)
        return subjects

    def get_exam_detail(self, exam_id: str) -> Optional[Exam]:
        """
        获取某个考试的详细情况, 包括考试科目, 参考班级等信息
        注意: 该接口不完全获取到考试科目的满分
        
        Args:
            exam_id (str): 为需要查询考试的id
        Return:
            Optional[Exam]: 考试详细信息, 若考试不存在则返回None
        """
        r = self._session.post(Url.GET_EXAM_DETAIL_URL, data={"examId": exam_id})
        data = r.json()
        if len(data["result"]) == 0:
            return None
        data = data["result"][0]  # TODO: 目前不考虑考试报告的情况
        exam = Exam(id=exam_id, name=data["examName"])
        subject_map: dict[str, Subject] = {}
        for each in data["classList"]:
            school = School(id=each["schoolId"])
            subjects = [Subject(id=inner["topicSetId"], name=inner["subjectName"], code=inner["subjectCode"], standard_score=inner.get("standScore", "0"), exam_id=exam_id) for inner in each["examSubjectList"]]
            for subject in subjects:
                if subject.id not in subject_map:
                    subject_map[subject.id] = subject
                else:
                    if subject.id != subject_map[subject.id].id:
                        raise ValueError(f"这种情况不应该发生, 请联系开发者，请将下面信息在issue中反馈:\n{ r.text }")
            if exam.schools.find_by_id(each["schoolId"]) is None:
                exam.schools.append(School(id=each["schoolId"]))
            exam.clazzs.append(StuClass(id=each["classId"], name=each["className"], grade=Grade(code=each["gradeCode"]), school=school))
            exam.grade_code = each["gradeCode"]  # 一般来说同一考试年级代码是一样的
        exam.subjects = ExtendedList(list(subject_map.values()))
        return exam

    def get_marking_progress(
        self,
        topic_set_id: str,
    ) -> List[MarkingProgress]:
        """
        获取某场考试指定科目阅卷情况
        Args:
            topic_set_id (str): 科目id
        Return:
            ExtendedList[MarkingProgress]
        """
        r = self._session.post(
            Url.GET_MARKING_PROGRESS_URL,
            data={"markingPaperId": topic_set_id},
            headers={"token": self.get_token()},
        )
        data = r.json()
        result: ExtendedList[MarkingProgress] = ExtendedList()
        for each in data:
            result.append(
                MarkingProgress(
                    topic_number=each["topicNumber"],
                    complete_rate=each["comleteRate"],  # 本来就是错误的拼写
                    complete_count=each["completeCount"],
                    all_count=each["allCount"],
                )
            )
        return result

    def _get_academic_info(self) -> List[AcademicInfo]:
        """
        获取学术信息用以获取教师考试
        """
        r = self._session.get(Url.GET_ACADEMIC_TERM_TEACHING_CYCLE_URL)
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
            year (int): 需要查询的年级, 如2022级则传入2022
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
        self._token = self._session.get(Url.GET_TOKEN_URL).json()["result"]
        return self._token