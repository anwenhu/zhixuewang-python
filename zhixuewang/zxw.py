import requests
import random
import json
from zhixuewang.models.exceptionsModel import (
    LoginError, UserDefunctError, UserNotFoundError, UserOrPassError, ArgError)
from zhixuewang.models.urlModel import *
from zhixuewang.models.personModel import Person
from zhixuewang.Student.student import Student
from zhixuewang.Teacher.teacher import Teacher, Headmaster, Headteacher

def login(username: str, password: str, type_: str = "auto") -> requests.session:
    """
    通过用户名和密码登录
    默认可支持zx和zxt开头的账号以及准考证号
    可通过改变type为id来支持以用户id登录
    :param username:
    :param password:
    :return:
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    r = session.get(SSO_URL)
    msg = r.text
    json_obj = json.loads(msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1000:
        raise LoginError(json_obj["data"])
    lt = json_obj["data"]["lt"]
    execution = json_obj["data"]["execution"]
    r = session.get(SSO_URL, params={
        "encode": "false",
        "sourceappname": "tkyh,tkyh",
        "_eventId": "submit",
        "appid": "zx-container-client",
        "client": "web",
        "type": "loginByNormal",
        "key": type_,
        "lt": lt,
        "execution": execution,
        "customLogoutUrl": "https://www.zhixue.com/login.html",
        "username": username,
        "password": password
    })
    msg = r.text
    json_obj = json.loads(msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1001:
        if json_obj["code"] == 1002:
            raise UserOrPassError()
        elif json_obj["code"] == 2009:
            raise UserNotFound()
        raise LoginError(json_obj["data"])
    ticket = json_obj["data"]["st"]
    session.post(SERVICE_URL, data={
        "action": "login",
        "ticket": json_obj["data"]["st"],
    })
    return session

def login_id(user_id: str, password: str) -> requests.session:
    """
    通过用户id和密码登录
    :param user_id: 用户id
    :param password: 密码
    :return
        返回session
    """
    return login(user_id, password, "id")

def get_user_id(username: str, password: str) -> str:
    """
    获取用户id
    :param username: 用户名
    :param password: 密码
    :return:
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    r = session.post(TEST_PASSWORD_URL, data={
        "loginName": username,
        "password": password,
        "code": ""
    })
    json_obj = r.json()   # {"data": ErrorMsg, "result": StatusCode}
    if json_obj.get("data"):
        return data["data"]
    elif json_obj["result"] != "success":
        raise UserOrPassError()
    return ""

def check_is_student(s: requests.session) -> bool:
    url = s.get("https://www.zhixue.com/container/container/index/").url
    return "student" in url

def get_roles(s: requests.session, user_id: str) -> str:
    """
    获取用户角色
    :param s: session
    :return
        返回用户角色
    """
    r = s.post("https://www.zhixue.com/portalcenter/teacher/getRoles/?t=1570180709979", data={
        "userId": user_id,
    })
    data = r.json()
    return [i["eName"] for i in data]
    
def get_student_id(user_id: str, password: str) -> Student:
    session = login_id(user_id, password)
    student = Student(session)
    return student._get_info()

def get_student(username: str, password: str) -> Student:
    session = login(username, password)
    student = Student(session)
    return student._get_info()

def get_teacher_id(user_id: str, password: str) -> Teacher:
    session = login_id(user_id, password)
    teacher = Teacher(session)
    return teacher._get_info()

def get_teacher(username: str, password: str) -> Teacher:
    session = login(username, password)
    teacher = Teacher(session)
    return teacher._get_info()

def Zhixuewang(username: str = None, password: str = None, user_id: str = None) -> Person:
    """
    通过(用户id, 密码)或(用户名, 密码)登录智学网
    :param username: 用户名
    :param password: 密码
    :param user_id: 用户id
    :return 
    """
    if not (password and any([username, user_id])):
        raise ArgError("请检查参数")
    if username:
        session = login(username, password)
    else:
        session = login_id(user_id, password)
    if check_is_student(session):
        return Student(session)._get_info()
    teacher = Teacher(session)._get_info()
    roles = get_roles(session, teacher.id)
    print(roles)
    if "headteacher" in roles:
        teacher = Headteacher(teacher)
    elif "headmaster" in roles:
        teacher = Headmaster(teacher)
    elif "teacher" in roles:
        pass
    else:
        raise Exception("账号是未知用户")
    return teacher._get_info()


def get_user_info_by_username(username: str) -> str:
    """
    (测试)通过用户名获取用户名字和id
    :param username: 用户名
    :return: 用户id
    """
    from PIL import Image
    import time
    from io import BytesIO
    import requests

    def get_captcha(s: requests.session):
        r = s.get("https://pass.changyan.com/kaptcha.jpg", params={
            "type": "normal",
            "d": time.time() * 1000
        })
        Image.open(BytesIO(r.content)).save("captcha.png")
        return input("请输入验证码").strip()

    def check_captcha(s: requests.session, captcha: str):
        r = s.post("https://pass.changyan.com/api/checkCaptcha", data={
            "t": "normal",
            "c": captcha
        })
        return r.json().get("ok")
    s = requests.session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"
    s.get("https://pass.changyan.com/forget/forget")
    while True:
        captcha = get_captcha(s)
        if check_captcha(s, captcha):
            break
    r = s.post("https://pass.changyan.com/forget/getUserInfo", data={
        "a": username,
        "p": captcha
    }, headers={
        "Referer": "https://pass.changyan.com/forget/forget"
    })
    data = r.json()
    if data["Code"] != 0:
        return False
    else:
        name = r.json()["Data"][0]["userName"]
    r = s.post("https://pass.changyan.com/forget/getUserPwdType", data={
        "u": "0"
    })
    return name, r.json()["Data"]["id"]



def rewrite_str(model):
    """
    重写类的__str__方法
    """
    def str_decorator(func):
        model.__str__ = func
        return func
    return str_decorator