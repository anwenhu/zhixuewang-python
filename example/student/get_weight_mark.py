from zhixuewang import rewrite_str, login_student
import zhixuewang


@rewrite_str(zhixuewang.models.Mark)
def _(self):
    score = 0
    for subject in self:
        if subject.subject.name == "语文":
            score += subject.score * 0.8
        elif subject.subject.name == "数学":
            score += subject.score * 0.7
        elif subject.subject.name == "英语":
            score += subject.score * 0.5
    return f"加权后的分数为: {score}"


if __name__ == "__main__":
    #请修改如下字段为你的账号和密码
    user = "114514"
    password = "1919810"
    if user == "114514" or password == "1919810":
        print("请修改源代码第20,21行，改为自己的账号和密码！")
    else:
        zxw = login_student(user, password)
        print(zxw.get_self_mark())