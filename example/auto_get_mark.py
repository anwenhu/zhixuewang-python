from zhixuewang import Zhixuewang
from zhixuewang.models.exceptionsModel import UserOrPassError
import time
import requests


def get_msg(mark):
    msg = f"{mark.name}:{mark.id}"
    for subject in mark:
        msg += "".join([
            "  \n",
            "# ",
            subject.subjectName,
            "  \n",
            "分数: ",
            str(subject.score),
            "  \n",
            "班级平均分: ",
            str(subject.classRank.avgScore),
            "  \n",
            "班级最高分: ",
            str(subject.classRank.highScore),
            "  \n",
            "班级最低分: ",
            str(subject.classRank.lowScore),
            "  \n",
            "班级排名: ",
            str(subject.classRank.rank),
            "  \n"
            "年级平均分: ",
            str(subject.gradeRank.avgScore),
            "  \n",
            "年级最高分: ",
            str(subject.gradeRank.highScore),
            "  \n",
            "年级最低分: ",
            str(subject.gradeRank.lowScore),
            "  \n",
        ])
    return msg


def send_mark(mark):
    r = requests.get(f"https://sc.ftqq.com/{desp}.send", params={
        "text":  "智学网出成绩了！",
        "desp":  get_msg(mark)
    })
    if not r.ok:
        time.sleep(5)
        send_mark(mark)


if __name__ == "__main__":
    with open("user", "r", encoding="utf8") as f:
        username = f.readline().strip()
        password = f.readline().strip()
        desp = f.readline().strip()
    zxw = Zhixuewang(username, password)
    # lastMark = zxw.get_self_mark()
    from zhixuewang.models.examModel import examMarkModel, subjectMarkModel, examModel
    exam = zxw.get_latest_exam()
    while True:
        new_exam = zxw.get_latest_exam()
        if new_exam != exam:
            print("已查到成绩!")
            send_mark(zxw.get_self_mark(new_exam))
        time.sleep(60 * 60)
