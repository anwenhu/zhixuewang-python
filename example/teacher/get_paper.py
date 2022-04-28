from zhixuewang import login
import os

if __name__ == "__main__":
    print("请先进行登录...")
    print("教师账号是：")
    uname = input()
    print("教师密码是：")
    upwd = input()
    print("学生账号是：")
    stuname = input()
    print("学生密码是：")
    stupwd = input()
    
    teacher = login(uname, upwd)
    student = login(stuname, stupwd)
    while True:
        print("保存位置：")
        save = input()
        print("考试名：" + student.get_exams()[0].name)
        subjects = student.get_subjects()
        for i in range(0, len(subjects)):
            print("顺序ID=" + str(i) + "    学科=" + str(subjects[i].name))
        
        print("请输入想查看的学科顺序id")
        subj_id = input()
        result = teacher.get_original_paper(student.id, subjects[int(subj_id)].id, save) #获得返回值
        if result != "OK":
            print("发生了错误，无法获得原卷。（可能是尚未生成或没有权限。）")
        else:
            os.startfile(save)
        print("是否继续？(y/n)")
        need_continue = input()
        if need_continue == "n" or need_continue == "N":
            exit(0)

