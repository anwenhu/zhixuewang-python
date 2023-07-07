from zhixuewang.urls import BASE_URL


class Url:
    INFO_URL = f"{BASE_URL}/container/container/student/account/"

    CHANGE_PASSWORD_URL = f"{BASE_URL}/portalcenter/home/updatePassword/"

    TEST_URL = f"{BASE_URL}/container/container/teacher/teacherAccountNew"

    GET_EXAM_URL = f"{BASE_URL}/classreport/class/classReportList/"
    GET_AcademicTermTeachingCycle_URL = f"{BASE_URL}/classreport/class/getAcademicTermTeachingCycle/"

    GET_REPORT_URL = f"{BASE_URL}/exportpaper/class/getExportStudentInfo"
    GET_MARKING_PROGRESS_URL = f"{BASE_URL}/marking/marking/markingProgressDetail"

    GET_EXAM_DETAIL_URL = f"{BASE_URL}/scanmuster/cloudRec/scanrecognition"

    GET_EXAM_SCHOOLS_URL = f"{BASE_URL}/exam/marking/schoolClass"
    GET_EXAM_SUBJECTS_URL = f"{BASE_URL}/configure/class/getSubjectsIncludeSubAndGroup"
    # 后必须接上paperId
    # ORIGINAL_PAPER_URL = f"{BASE_URL}/classreport/class/student/checksheet/?userId="
    ORIGINAL_PAPER_URL = f"{BASE_URL}/classreport/class/student/checksheet/"
