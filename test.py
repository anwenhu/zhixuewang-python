from zhixuewang import get_session, login_student
from getpass import getpass
import os

#
# 给你个老师账号:
#
tch_session = get_session("zxt359439", "mn3966")
# i = input("1. 智学网账号密码登录\n 2. 直接输入相关数据(考试班级id, 各科目id, )")
username = input("请输入智学网账号:")
password = getpass()
zxw = login_student(username, password)
classids = ",".join([i.id for i in zxw.get_classmates()])
os.system("cls")
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
    subjects = zxw.get_subjects(exam)
    for subject in subjects:
        r = tch_session.post(f"https://www.zhixue.com/exportpaper/class/getExportStudentInfo/?&classId={classids}&topicSetId={subject.id}&topicNumber=0&type=export_single_paper_zip&studentNum=&startScore=1&endScore=1000")
        print(r.json())
        exit()
    while True:
        b = input("是否再次查询(Y为是,N为不是)").strip()
        if b != "Y" and b != "N":
            print("输入有误")
        if b == "N":
            continued = False
        break
