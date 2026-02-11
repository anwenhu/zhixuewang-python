# 自动下载智学网作业资源
# 每分钟检测一次是否有新作业生成, 若有则下载到目录中

import time

from zhixuewang import login_cookie

cookie = ""     # 智学网cookie
path = ""       # 下载到哪个目录

zxw = login_cookie(cookie).to_student()
ids = []
while True:
    hws = zxw.get_homeworks()
    for homework in hws:
        if homework.id not in ids:
            for resource in zxw.get_homework_resources(homework):
                resource.download(path)
            ids.append(homework.id)
    time.sleep(60)
