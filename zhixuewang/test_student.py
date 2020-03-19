import pytest
from zhixuewang import login, login_student, login_student_id
# from zhixuewang.student import FriendMsg
username, password, user_id = "", "", ""


def setup_module():
    global username, password, user_id
    with open("user", "r", encoding="utf8") as f:
        username, password, user_id = f.readline().strip().split(" ")


class TestStudent:
    def setup_class(self):
        self.zxw = login_student(username, password)
        self.exams = self.zxw.get_exams()

    def test_login(self):
        assert login(username, password).id == user_id

    def test_login_student(self):
        assert login_student(username, password).id == user_id

    def test_login_student_id(self):
        login_student_id(user_id, password)

    def test_get_exams(self):
        assert self.zxw.get_exams()

    def test_get_exam(self):
        assert self.zxw.get_exam(self.exams[0]) == self.exams[0]
        assert self.zxw.get_exam(self.exams[0].id) == self.exams[0]
        assert self.zxw.get_exam(self.exams[0].name) == self.exams[0]

    def test_get_latest_exam(self):
        exams = self.zxw.get_exams()
        assert self.zxw.get_latest_exam() == exams[0]

    def test_get_self_mark(self):
        assert self.zxw.get_self_mark().exam == self.exams[0]
        assert self.zxw.get_self_mark(self.exams[0]).exam == self.exams[0]
        assert self.zxw.get_self_mark(self.exams[-1]).exam == self.exams[-1]

    def test_get_subjects(self):
        subjects = self.zxw.get_subjects()
        for subject in subjects:
            assert subject.exam == self.exams[0]

        subjects = self.zxw.get_subjects(self.exams[-1])
        for subject in subjects:
            assert subject.exam == self.exams[-1]

    def test_get_subject(self):
        subject = self.zxw.get_subject("语文")
        assert subject.name == "语文" and subject.exam == self.exams[0]

        subject = self.zxw.get_subject("数学", self.exams[1])
        assert subject.name == "数学" and subject.exam == self.exams[1]

        subject = self.zxw.get_subject("英语", self.exams[2].id)
        assert subject.name == "英语" and subject.exam == self.exams[2]

        subject = self.zxw.get_subject("物理", self.exams[3].name)
        assert subject.name == "物理" and subject.exam == self.exams[3]

        subjects = self.zxw.get_subjects()
        subject = self.zxw.get_subject(subjects[0])
        assert subject == subjects[0] and subject.exam == self.exams[0]

        subject = self.zxw.get_subject(subjects[1].id)
        assert subject == subjects[1] and subject.exam == self.exams[0]

    def test_get_original(self):
        self.zxw.get_original("语文")

        self.zxw.get_original("数学", self.exams[1])

        self.zxw.get_original("英语", self.exams[2].id)

        self.zxw.get_original("物理", self.exams[3].name)

        self.zxw.get_original("化学", self.exams[4])

        subjects = self.zxw.get_subjects()
        self.zxw.get_original(subjects[0])

        self.zxw.get_original(subjects[1].id)

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
