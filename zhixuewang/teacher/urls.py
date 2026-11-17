from zhixuewang.urls import BASE_URL

GECE_URL = "https://gece.zhixue.com"


class Url:
    INFO_URL = f"{BASE_URL}/container/container/student/account/"

    CHANGE_PASSWORD_URL = f"{BASE_URL}/portalcenter/home/updatePassword/"

    TEST_URL = f"{BASE_URL}/container/container/teacher/teacherAccountNew"

    GET_EXAM_URL = f"{BASE_URL}/classreport/class/classReportList/"
    GET_ACADEMIC_TERM_TEACHING_CYCLE_URL = f"{BASE_URL}/api-classreport/class/getAcademicTermTeachingCycle/"

    GET_REPORT_URL = f"{BASE_URL}/exportpaper/class/getExportStudentInfo"
    GET_MARKING_PROGRESS_URL = "https://pt-ali-bj-re.zhixue.com/marking/marking/markingTopicProgress/"

    GET_EXAMS_URL = f"{BASE_URL}/api-classreport/class/classReportList/"
    GET_EXAM_DETAIL_URL = f"{BASE_URL}/api-classreport/class/examInfo/"

    GET_EXAM_SCHOOLS_URL = f"{BASE_URL}/exam/marking/schoolClass"
    GET_EXAM_SUBJECTS_URL = f"{BASE_URL}/configure/class/getSubjectsIncludeSubAndGroup"
    # 后必须接上paperId
    # ORIGINAL_PAPER_URL = f"{BASE_URL}/classreport/class/student/checksheet/?userId="
    ORIGINAL_PAPER_URL = f"{BASE_URL}/classreport/class/student/checksheet/"

    GET_ADVANCED_INFORMATION_URL = f"{BASE_URL}/paperfresh/api/common/getCurrentUser"
    GET_STUDENT_STATUS_URL = f"{BASE_URL}/api-teacher/home/getStudentStatus"
    
    GET_TOKEN_URL = f"{BASE_URL}/container/app/token/getToken"
    
    # 新版作业相关 API
    GET_HOMEWORK_LIST_URL = f"{GECE_URL}/api-platform-report/report/list/teacher"
    GET_HOMEWORK_ACADEMIC_YEAR_TERM_URL = f"{GECE_URL}/api-school-book/report/list/getAcademicYearTerm"
    GET_HOMEWORK_GRADE_LIST_URL = f"{GECE_URL}/api-school-book/homework/getBaseGradeList"
    GET_HOMEWORK_DETAIL_URL = f"{GECE_URL}/api-platform-report/report/head/getHomework"
    