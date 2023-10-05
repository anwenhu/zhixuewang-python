from zhixuewang import rewrite_str, login_student
from zhixuewang.models import Mark


@rewrite_str(Mark)
def _(self):
    score = 0
    for subject in self:
        if subject.subject.name == "语文":
            score += subject.score * 0.8
        elif subject.subject.name == "数学":
            score += subject.score * 0.7
        elif subject.subject.name == "英语":
            score += subject.score * 0.5
    return f"加权后的分数为: {score}"  # 权重: 语文 0.8; 数学 0.7; 英语 0.5; 其他科 0


if __name__ == "__main__":
    username = input("请输入用户名:").strip()
    password = input("请输入密码:").strip()
    zxw = login_student(username, password)
    print(zxw.get_self_mark())
