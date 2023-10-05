from zhixuewang import login_student, login_teacher
import os

if __name__ == "__main__":
    uname = input("请输入一个教师账号：").strip()
    upwd = input("请输入一个教师密码：").strip()
    stuname = input("请输入要查询的学生账号：").strip()
    stupwd = input("请输入要查询的学生密码：").strip()

    teacher = login_teacher(uname, upwd)
    student = login_student(stuname, stupwd)
    while True:
        save = input("保存到哪个文件: ")
        print("考试名：" + student.get_page_exam(1)[0][0].name)
        subjects = student.get_subjects()
        for i in range(0, len(subjects)):
            print(f"顺序ID={i}    学科={subjects[i].name}")

        print("请输入想查看的学科顺序id")
        subj_id = input()
        result = teacher.get_original_paper(student.id, subjects[int(subj_id)].id, save)  # 获得返回值
        if not result:
            print("发生了错误，无法获得原卷。（可能是尚未生成或没有权限。）")
        else:
            os.startfile(save)
        print("是否继续？(y/n)")
        need_continue = input()
        if need_continue == "n" or need_continue == "N":
            exit(0)
