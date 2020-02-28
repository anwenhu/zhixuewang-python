from zhixuewang.Teacher.exam import ExtraExam
from zhixuewang.Teacher.models.urlModel import TEST_URL
from zhixuewang.Teacher.models.personModel import TeaPerson

class Teacher(TeaPerson, ExtraExam):
    def __init__(self, session):
        super(TeaPerson, self).__init__()
        self._session = session
        self.role = "teacher"

    def _get_info(self):
        r = self._session.get(TEST_URL, headers={
            "referer": "https://www.zhixue.com/container/container/teacher/index/"
        })
        json_data = r.json()["teacher"]
        self.email = json_data.get("email")
        self.gender = "男" if json_data["gender"] == "1" else "女"
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.name = json_data.get("name")
        return self



# 校长


class Headmaster(Teacher):
    def __init__(self, session):
        super().__init__(session)
        self.role = "headmaster"




# 年级主任 / 班主任
class Headteacher(Teacher):
    def __init__(self, session):
        super().__init__(session)
        self.role = "headteacher"
