from zhixuewang import login, login_student, login_student_id, load_account
# from zhixuewang.student import FriendMsg
username = "None"
password = "None"


def setup_module():
    with open("user", "r", encoding="utf8") as f:
        global username, password
        username, password = f.read().split(",")

class TestStudent:
    def setup_class(self):
        self.zxw = login_student(username, password)

    def test_login_student(self):
        assert login_student(username, password).code == username

    def test_login_student_id(self):
        pass

    def test_get_exams(self):
        assert self.zxw.get_exams()

    def test_get_exam(self):
        assert self.zxw.get_exam()

    def test_get_latest_exam(self):
        assert self.zxw.get_latest_exam()

    def test_get_self_mark(self):
        assert self.zxw.get_self_mark()

    def test_get_subjects(self):
        assert self.zxw.get_subjects()

    def test_get_subject(self):
        assert self.zxw.get_subject("语文").name == "语文"

    def test_get_original(self):
        assert self.zxw.get_original("语文")

    def test_get_clazzs(self):
        for clazz in self.zxw.get_clazzs():
            assert clazz.grade == self.zxw.clazz.grade and clazz.school == self.zxw.clazz.school

    def test_get_clazz(self):
        clazzs = self.zxw.get_clazzs()
        assert self.zxw.get_clazz() == self.zxw.clazz
        assert self.zxw.get_clazz(clazzs[0]) == clazzs[0]
        assert self.zxw.get_clazz(clazzs[1].id) == clazzs[1]
        assert self.zxw.get_clazz(clazzs[2].name) == clazzs[2]

    def test_get_classmates(self):
        clazzs = self.zxw.get_clazzs()
        assert self.zxw.get_classmates()[0].clazz == self.zxw.clazz
        assert self.zxw.get_classmates(clazzs[0])[0].clazz == clazzs[0]
        assert self.zxw.get_classmates(clazzs[1].id)[0].clazz == clazzs[1]
        assert self.zxw.get_classmates(clazzs[2].name)[0].clazz == clazzs[2]

    def test_get_friends(self):
        self.zxw.get_friends()

    def test_invite_friend(self):
        pass

    def test_remove_friend(self):
        pass
