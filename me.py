from zhixuewang import Zhixuewang

username = input("请输入用户名:")
password = input("请输入密码：")
zxw = Zhixuewang(username, password)
for exam in zxw.get_exams():
    print(exam.id)
    print(exam.name)
    # print(response.json())
# # print("%s:" % grades.pop("examName"))
# #
# #
# # for k, v in grades.items():
# #     print("%s:\n\t分数:%s" % (k, v.score))
# #     print("\t班级最高分:%s" % v.classRank.highScore)
# #     print("\t班级平均分:%s" % v.classRank.avgScore)
# #     print("\t班级排名:%s" % v.classRank.rank)
# #     print("\t年级平均分:%s" % v.gradeRank.avgScore)
# #     print("\t年级最高分:%s" % v.gradeRank.highScore)
# #
#
#
