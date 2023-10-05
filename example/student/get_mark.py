# 获取成绩
from zhixuewang import login_student
import os

if __name__ == "__main__":
    username = input("请输入用户名:")
    password = input("请输入密码:")
    zxw = login_student(username, password)
    os.system("cls")
    print("登录成功. 正在抓取考试列表...")
    exams = zxw.get_exams()
    if len(exams) == 0:
        print("你还没有考试呢~")
    continued = True
    while continued:
        print("考试列表:")
        for i, exam in enumerate(exams):
            print(f"{i}. {exam.name}")
        while True:
            i = input("请输入编号:").strip()
            if (not i.isdigit()) or int(i) < 0 or int(i) > len(exams) - 1:
                print("输入有误, 请重新输入")
            else:
                break
        print("正在查询成绩...")
        exam = exams[int(i)]
        print(zxw.get_self_mark(exam))
        while True:
            b = input("是否再次查询(Y为是,N为不是)").strip()
            if b != "Y" and b != "N":
                print("输入有误")
                continue
            if b == "N":
                continued = False
            break
