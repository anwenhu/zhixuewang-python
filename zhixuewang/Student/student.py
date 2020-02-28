from zhixuewang.Student.exam import ExtraExam
from zhixuewang.Student.person import ExtraPerson
from zhixuewang.Student.models.urlModel import INFO_URL, CHANGE_PASSWORD_URL
from zhixuewang.Student.models.personModel import StuPerson
from zhixuewang.models.personModel import StuClass, School, Sex, Grade, Phase
from zhixuewang.models.exceptionsModel import UserDefunctError

class Student(StuPerson, ExtraExam, ExtraPerson):
    def __init__(self, session):
        super(StuPerson, self).__init__()
        self._session = session
        self.username = ""
        self.role = "student"

    def _get_info(self):
        """
        获取账户基本信息, 如用户id, 姓名, 学校等
        :return:
        """
        r = self._session.get(INFO_URL, params={
           # "userId": self.id
        })
        json_data = r.json()["student"]
        if not json_data.get("clazz", False):
            raise UserDefunctError()
        self.code = json_data.get("code")
        self.name = json_data.get("name")
        self.avatar = json_data.get("avatar")
        self.gender = Sex.BOY if json_data.get("gender") == "1" else Sex.GIRL
        self.username = json_data.get("loginName")
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.email = json_data.get("email")
        self.qq_number = json_data.get("im")
        self.clazz = StuClass(
            id=json_data["clazz"]["id"],
            name=json_data["clazz"]["name"],
            school=School(
                id=json_data["clazz"]["division"]["school"]["id"],
                name=json_data["clazz"]["division"]["school"]["name"]
            ),
            grade=Grade(
                code=json_data["clazz"]["division"]["grade"]["code"],
                name=json_data["clazz"]["division"]["grade"]["name"],
                phase=Phase(
                    code=json_data["clazz"]["division"]["grade"]["phase"]["code"],
                    name=json_data["clazz"]["division"]["grade"]["phase"]["name"]
                )
            )
        )
        birthday = int(int(json_data.get("birthday", 0)) / 1000)
        self.birthday = birthday
        return self
