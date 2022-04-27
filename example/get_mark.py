from zhixuewang import login_student
from getpass import getpass
from zhixuewang import rewrite_str
import zhixuewang.models
import os


@rewrite_str(zhixuewang.models.Mark) #此处重写str方法
# 旧版本（1.0.X）会格式化后输出，新版本(1.1.X)中get_self_mark()方法不再格式化，所以在此重写方法，友好输出。
def _(self):
    msg = f"{self.exam.name}:{self.exam.id}"
    for subject in self:
        msg += "".join([
            "  \n",
            f"# {subject.subject.name}  \n",
            f"分数: {subject.score}  \n",
        ])
    return msg

if __name__ == "__main__":
    username = input("请输入用户名:")
    password = getpass()
    zxw = login_student(username, password)
    os.system("clear")
    print("登录成功. 正在抓取考试列表...")
    exams = zxw.get_exams()
    if len(exams) == 0:
        print("你还没有考试呢.")
    continued = True
    while continued:
        print("考试列表:")
        for i, exam in enumerate(exams):
            print(f"{i}. {exam.name}")
        msg = "请输入编号:"
        while True:
            i = input(msg).strip()
            if (not i.isdigit()) or int(i) < 0 or int(i) > len(exams) - 1:
                print("输入有误")
                msg = "请重新输入:"
            else:
                break
        print("正在查询成绩...")
        i = int(i)
        exam = exams[i]
        print("成绩为:")
        print("\n")
        print(zxw.get_self_mark())
        while True:
            b = input("是否再次查询(Y为是,N为不是)").strip()
            if b != "Y" and b != "N":
                print("输入有误")
            if b == "N":
                continued = False
            break
