from ..models.userModel import User
from .models.urlModel import TEST_URL


class Teacher(User):
    def __init__(self, session):
        super().__init__(session)
        self.role = "teacher"

    def _get_info(self):
        r = self._session.get(TEST_URL, headers={
            "referer": "https://www.zhixue.com/container/container/teacher/index/"
        })
        json_data = r.json()["teacher"]
        print(json_data)
        self.email = json_data.get("email")
        self.gender = "男" if json_data["gender"] == "1" else "女"
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.name = json_data.get("name")
        self.school.id = json_data.get("school")["id"]
        self.school.name = json_data.get("school")["name"]
        print(json_data)
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
