from zhixuewang import login_student
from getpass import getpass
import os

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
        print(zxw.get_self_mark())
        while True:
            b = input("是否再次查询(Y为是,N为不是)").strip()
            if b != "Y" and b != "N":
                print("输入有误")
            if b == "N":
                continued = False
            break
