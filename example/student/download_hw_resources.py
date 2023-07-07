### 自动下载智学网作业资源

from zhixuewang import login_student
import time

username = ""
password = ""
path = ""

zxw = login_student(username, password)
ids = []
while True:
    hws = zxw.get_homeworks()
    for homework in hws:
        if homework.id not in ids:
            for resource in zxw.get_homework_resources(homework):
                resource.download(path)
            ids.append(homework.id)
    time.sleep(60)
