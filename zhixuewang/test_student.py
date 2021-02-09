from zhixuewang import login, login_student, login_student_id
# from zhixuewang.student import FriendMsg
username, password, user_id, check_exam_name, check_exam_id, check_chinese_id, check_math_id, check_english_id, check_chinese_score, check_math_score, check_english_score = "", "", "", "", "", "", "", "", "", "", ""



def setup_module():
    global username, password, user_id, check_exam_name, check_exam_id, check_chinese_id, check_math_id, check_english_id, check_chinese_score, check_math_score, check_english_score
    with open("user", "r", encoding="utf8") as f:
        username, password, user_id, check_exam_name, check_exam_id, check_chinese_id, check_math_id, check_english_id, check_chinese_score, check_math_score, check_english_score = f.readline().strip().split(" ")


class TestStudent:
    def setup_class(self):
        self.zxw = login_student(username, password)

    def test_login(self):
        assert login(username, password).id == user_id

    def test_login_student(self):
        assert login_student(username, password).id == user_id

    def test_login_student_id(self):
        login_student_id(user_id, password)

    def test_get_exams(self):
        assert self.zxw.get_exams()

    def test_get_exam(self):
        assert self.zxw.get_exam()
        assert self.zxw.get_exam(check_exam_name).id == check_exam_id
        assert self.zxw.get_exam(check_exam_id).name == check_exam_name

    def test_get_latest_exam(self):
        assert self.zxw.get_latest_exam()

    def test_get_self_mark(self):
        assert self.zxw.get_self_mark()
        assert self.zxw.get_self_mark(check_exam_name).find(lambda x: x.subject.name == "语文").score == int(check_chinese_score)
        assert self.zxw.get_self_mark(check_exam_id).find(lambda x: x.subject.name == "数学").score == int(check_math_score)

    def test_get_subjects(self):
        assert self.zxw.get_subjects()

    def test_get_subject(self):
        subject = self.zxw.get_subject("语文", check_exam_name)
        assert subject.name == "语文" and subject.exam.id == check_exam_id

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
