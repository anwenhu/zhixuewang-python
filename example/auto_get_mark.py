import zhixuewang
import time
import requests
from zhixuewang import login_student, rewrite_str


@rewrite_str(zhixuewang.models.Mark)
def _(self):
    msg = f"{self.exam.name}:{self.exam.id}"
    for subject in self:
        msg += "".join([
            "  \n",
            f"# {subject.subject.name}  \n",
            f"分数: {subject.score}  \n",
        ])
    return msg


def send_mark(mark): #此处通过推送服务发送消息，需要自行注册（已更新到新版API）
    r = requests.get(f"https://sctapi.ftqq.com/{desp}.send",
                     params={
                         "title": "智学网出成绩了！",
                         "desp": str(mark)
                     })
    if not r.ok:
        time.sleep(5)
        send_mark(mark)


if __name__ == "__main__":
    
    with open("user", "r", encoding="utf8") as f: #第一行为账号，第二行为密码，第三行为推送sendkey
        username = f.readline().strip()
        password = f.readline().strip()
        desp = f.readline().strip()
    zxw = login_student(username, password)
    exam = zxw.get_latest_exam()
    while True:
        new_exam = zxw.get_latest_exam()
        if new_exam != exam:
            print("已查到成绩!")
            send_mark(zxw.get_self_mark(new_exam))
        time.sleep(60 * 60)
