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
    Grade,
    TextBook,
    StuPerson,
    TextBookChapter
)
from zhixuewang.teacher.models import (
    MarkingProgress, 
    PageExam, 
    TeaPerson, 
    AcademicInfo, 
    # 负责选题的部分以Question开头
    Question, 
    QuestionDifficulty, 
    QuestionKnowledges, 
    QuestionSection,
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

        if (
            adv_result["school"] == None
            or adv_result["curSubject"] == None
            or adv_result["grade"] == None
            or adv_result["textBookVersion"] == None
            or adv_result == None
            or adv_result["grade"] == None
        ):
            print(
                f"教师高级信息传回空值，原始JSON数据为 School: {adv_result['school']} curSubject: {adv_result['curSubject']} grade: {adv_result['grade']}  textBook: {adv_result['textBookVersion']}"
            )
        try:
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
                code=str(adv_result["textBookVersion"]["code"]),
                name=adv_result["textBookVersion"]["name"],
                version=adv_result["bookVersion"]["name"],
                versionCode=str(adv_result["bookVersion"]["code"]),
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
        except BaseException as e:
            print(str(e))
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

    #! 人教版 272
    def get_problems(
            self, 
            subjectCode: str, 
            phaseCode: str, 
            chapterCode: str, 
            pressCode: str, 
            areas: str = "", 
            difficultyCode: str = "",
            pageSize: str = "10",
            pageIndex: str = "1",
            questionMode: str = "") -> List[Question]:
        """
            subjectCode: 学科ID，例如高中地理为14\n
            phaseCode: 不清楚，反正高中是05\n
            pressCode: 出版社编号，使用search_press\n
            areas: 限定区域（多个区域例如浙江江苏请传入`450000,210000,310000`）\n
            chapterCode: 当前章节编号（使用get_available_chapters获取）\n
            difficultyCode: 难度代码（hard, easy, normal）\n
            questionMode: 题目类型（单选`singleChoice`，多选`multiChoice`，综合`complex`，全部`all`）\n
            pageSize: 每页展示多少题\n
            pageIndex: 控制这是第几页

            Return:
                `Question`和题目总数(int)

            Tips:
                请使用search_press和search_subjectcode
        """
        #region diff处理
        difficulty = ""
        if difficultyCode == "hard":
            difficulty = "01;02"
        elif difficultyCode == "normal":
            difficulty = "03"
        elif difficultyCode == "easy":
            difficulty = "04;05"
        sectionCode = ""
        if questionMode == "singleChoice":
            sectionCode = "140500n"
        elif questionMode == "all" or questionMode == "":
            sectionCode = ""
        elif questionMode == "multiChoice":
            sectionCode = "140501n"
        elif questionMode == "complex":
            sectionCode = "140502n"
        #endregion

        params_data = {
            "difficultyCode": difficulty,
            "chapterCode": chapterCode,
            "pageIndex": pageIndex,
            "pageSize": pageSize,
            "phaseCode": phaseCode,
            "subjectCode": subjectCode,
            "pressCode": pressCode,
            "areas": areas,
            "sectionCode": sectionCode,
            "keywordSearchField": "topic",
            "keyWord": " ",
            "excludePapers": "",
            "year": "",
            "isNoveltyQuestion": "",
            "sortField": "lastModify",
            "topicClassTags": "",
            "thinkMethods": "",
            "typicalSceneCode": "",
            "zfSolveMethods": "",
            "subjectAttainments": "",
            "tfSolveMethods": "",
            "sceneTypes": ""
        }
        response = self._session.post(Url.GET_TOPICS_URL, data=params_data, headers={ # 此处智学网会判定Content-Type和Referer，故手动添加
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "https://www.zhixue.com/paperfresh/dist/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Origin": "https://www.zhixue.com"
        }).json()
        if response['errorCode'] != 0:
            raise ValueError(f"获取题目时发生错误：{response['errorInfo']}(错误代码{response['errorCode']})")
        total = int(response['result']['pager']['totalCount'])
        questions = response['result']['pager']['list']
        ret: list = [] # type: Question
        for q in questions:
            retsult :Question = Question("", "", None, [], None, [], [], [], "", 0.0, "", "", "", "", False)
            retSection :QuestionSection = QuestionSection("", "", "", "", 0, False, 0)
            retDiff :QuestionDifficulty = QuestionDifficulty("", "", 0)
            retKnowledges: QuestionKnowledges = QuestionKnowledges("", "", 0.0)
            #region 基本信息设置
            retsult.id = q['id']
            retsult.number = q['number']
            retsult.createTime = q['creatTime']
            retsult.isXGKQuestion = q['xgkTopic']
            retsult.score = q['score']
            #endregion
            #region Section设置
            retSection.categoryCode = q['section']['categoryCode']
            retSection.categoryName = q['section']['categoryName']
            retSection.code = q['section']['code']
            retSection.name = q['section']['name']
            retSection.sort = q['section']['sort']
            retSection.isSubjective = q['section']['isSubjective']
            retSection.score = q['section']['score']
            #endregion
            #region 难度信息设置
            retDiff.code = q['difficulty']['code']
            retDiff.name = q['difficulty']['name']
            retDiff.value = q['difficulty']['value']
            #endregion
            #region 知识信息设置
            #!TODO 暂不支持读取knowledges.ability
            for knowl in q['knowledges']:
                retKnowledges.code = knowl['code']
                retKnowledges.name = knowl['name']
                retKnowledges.weight = knowl['weight']
                retsult.knowledges.append(retKnowledges)
                retKnowledges = QuestionKnowledges("", "", 0.0)
            for knowl in q['commonKnowledges']:
                retKnowledges.code = knowl['code']
                retKnowledges.name = knowl['name']
                retKnowledges.weight = knowl['weight']
                retsult.knowledges.append(retKnowledges)
                retKnowledges = QuestionKnowledges("", "", 0.0)      
            #endregion
            #region 答案与题干、使用学校设置
            retsult.contentHtml = q['originalStruct']['contentHtml']
            retsult.paperName = q['paperName']
            retsult.answerImg = q['answerImg']
            retsult.analysisImg = q['analysisImg']
            for paper in q['papers']:
                retsult.usedPapers.append(paper["name"])
            #endregion
            #region 信息整合
            retsult.difficulty = retDiff
            retsult.section = retSection
            #endregion
            ret.append(retsult)
        return ret, total

    #region 搜索部分
    def search_press(self, pressString: str) -> str:
        '''通过出版社名称搜索对应的出版社代码\n
        传入例子：人教新课标、人教数学A新课标、北师大数学新课标
        '''
        if "人教新课标" or "人教" in pressString:
            return "272"
        elif "北师大数学新课标" in pressString:
            return "278"
        elif "人教数学新课标" in pressString:
            return "273"
        elif "苏教新课标" in pressString:
            return "282"
        elif "浙科新课标" in pressString:
            return "294"     
        elif "鲁科新课标" in pressString:
            return "283"
        
        
    def search_subjectcode(self, subjName: str) -> str:
        '''通过学科名称搜索对应的学科代码'''
        if '高中地理' in subjName:
            return "14"
        elif "高中历史" in subjName:
            return "12"
        elif "高中思想政治" in subjName:
            return "103"
        elif "高中生物" in subjName:
            return "13"
        elif "高中化学" in subjName:
            return "06"
        elif "高中物理" in subjName:
            return "05"
        elif "高中英语" in subjName:
            return "03" 
        elif "高中数学" in subjName:
            return "02"
        elif "高中语文" in subjName:
            return "01" 
        
    #endregion
    def change_subject(self, subject: Subject, phaseCode:str):
        '''更换教师当前的学科'''
        if subject.code == self.currentSubject.code:
            return
        self._session.post(Url.SWITCH_SUBJECT_URL, data={"phaseCode": phaseCode, "subjectCode": subject.code})
        self.set_base_info()

    def get_available_textbook(self, pressCode: str) -> List[TextBook]:
        '''
        获得教师`curSubject`所对应的教科书\n
        `pressCode`：出版社代码，人教为272
        '''
        response = self._session.post(Url.GET_TEXTBOOK_URL, 
                    params={'pressCode': pressCode},
                    headers= { 
                        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                        "Referer": "https://www.zhixue.com/paperfresh/dist/",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
                        "Origin": "https://www.zhixue.com"}).json()
        if response['errorCode'] != 0:
            raise ValueError(f"获取教科书时发生错误：{response['errorInfo']}(错误代码{response['errorCode']})")
        result = response['result']
        ret: List[TextBook] = []
        for node in result:
            childs: list = []
            for child in node['children']:
                # 遍历单元
                childs.append(TextBookChapter(child['id'], child['name'], child['nodeType']))
                if child["children"] != None: # 下面还有课程
                    for corChild in child['children']:
                        # 遍历课程
                        childs.append(TextBookChapter(corChild['id'], corChild['name'], corChild['nodeType']))
            #!TODO 暂时不支持获取学科，使用教师的currentSubject替代
            ret.append(TextBook(node['id'], node['name'], version = None, versionCode= None, pressCode= pressCode, availableChapters = childs))
        return ret

    def get_token(self) -> str:
        if self._token is not None:
            return self._token
        r = self._session.get("https://www.zhixue.com/container/app/token/getToken")
        self._token = r.json()["result"]
        return self._token
