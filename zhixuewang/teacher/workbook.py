from typing import List
from requests import Session
from zhixuewang.models import (
    Subject,
    TextBook,
    TextBookChapter
)
from zhixuewang.teacher.models import (
    # 负责选题的部分以Question开头
    Question, 
    QuestionDifficulty, 
    QuestionKnowledges, 
    QuestionSection,
    Knowledge
)
from zhixuewang.teacher.urls import Url

class Workbook:
    _session: Session = None
    def __init__(self, teacherSession):
        self._session = teacherSession
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
            questionMode: str = "",
            useKnowledgeToSearch: bool = False,
            knowledges: list = [],
            year: str = "") -> List[Question]:
        """
            subjectCode: 学科ID，例如高中地理为14\n
            phaseCode: 不清楚，反正高中是05\n
            pressCode: 出版社编号，使用search_press\n
            areas: 限定区域（多个区域例如浙江江苏请传入`450000,210000,310000`）\n
            chapterCode: 当前章节编号（使用get_available_chapters获取）\n
            difficultyCode: 难度代码（hard, easy, normal）\n
            questionMode: 题目类型（单选`singleChoice`，多选`multiChoice`，综合`complex`，全部`all`）\n
            pageSize: 每页展示多少题\n
            pageIndex: 控制这是第几页\n
            useKnowledgeToSearch: 控制是否使用知识点出题功能\n
            knowledges: 需要出题的知识点ID\n
            year: 限定题目的年份，默认为不限制

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
            "year": year,
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
        if useKnowledgeToSearch:
            params_data["knowledgeType"] = 0
            request_knowledgestr = "["
            for reqKnow in knowledges:
                request_knowledgestr += "\"" + reqKnow + "\","
            request_knowledgestr += "]"
            request_knowledgestr = request_knowledgestr.replace(",]", "]") # 去除最后一个
            if len(knowledges) == 1: # 单选知识点
                params_data["knowledgeSelectType"] = "0"
            else:
                params_data["knowledgeSelectType"] = "1"
            params_data["knowledgeCode"] = request_knowledgestr
            del params_data["chapterCode"]
            
        response = self._session.post(Url.GET_TOPICS_URL, data=params_data, headers={ # 此处智学网会判定Content-Type和Referer，故手动添加
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "https://www.zhixue.com/paperfresh/dist/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Origin": "https://www.zhixue.com"
        }).json()
        if response['errorCode'] != 0:
            raise ValueError(f"获取题目时发生错误：{response['errorInfo']}(错误代码{response['errorCode']})")
        #print(response['result'])
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

    def get_knowledges(self) -> List[Knowledge]:
        '''
        获取知识点
        '''
        response = self._session.post(Url.GET_KNOWLEDGES_URL, 
            headers= { 
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Referer": "https://www.zhixue.com/paperfresh/dist/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
                "Origin": "https://www.zhixue.com"}).json()
        if response['errorCode'] != 0:
            raise ValueError(f"获取知识点时发生错误：{response['errorInfo']}(错误代码{response['errorCode']})")
        result = response['result']
        childs: list = []
        for node in result:
            childs.append(Knowledge(node["id"], node["name"], False, ""))
            for child in node['children']:
                # 遍历大知识点
                if child["children"] != None: # 下面还有知识点
                    for corChild in child['children']:
                        childs.append(Knowledge(corChild["id"], corChild["name"], True, node["id"]))
            #!TODO 暂时不支持获取学科，使用教师的currentSubject替代
        return childs