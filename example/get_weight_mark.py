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
    zxw = login_student("zx39813588", "SYJ39813588")
    print(zxw.get_self_mark())