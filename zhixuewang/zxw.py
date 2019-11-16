import requests
import random
import json
from .models.exceptionsModel import (
    LoginError, UserDefunctError, UserNotFound, UserOrPassError, ArgError)
from .models.userModel import User
from .models.urlModel import *
from .Student.student import Student
from .Teacher.teacher import Teacher, Headmaster, Headteacher


def login_id(user_id: str, password: str) -> requests.session:
    """
    通过用户id和密码登录
    :param user_id: 用户id
    :param password: 密码
    :return
        返回session
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    msg = session.get(SSO_URL).text
    json_obj = json.loads(
        msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1000:
        raise LoginError(json_obj["data"])
    data = json_obj["data"]
    msg = session.get(SSO_URL,
                      params={
                          "username": user_id,
                          "password": password,
                          "sourceappname": "tkyh,tkyh",
                          "key": "id",
                          "_eventId": "submit",
                          "lt": data["lt"],
                          "execution": data["execution"],
                          "encode": False
                      }).text
    json_obj = json.loads(
        msg[msg.find("{"): msg.rfind("}") + 1].replace("\\", ""))
    if json_obj["code"] != 1001:
        if json_obj["code"] == 1002:
            raise UserOrPassError()
        elif json_obj["code"] == 2009:
            raise UserNotFound()
        raise LoginError(json_obj["data"])
    session.post(SERVICE_URL, data={
        "action": "login",
        "username": user_id,
        "password": password,
        "ticket": json_obj["data"]["st"],
    })
    return session


def get_user_id(user_name: str, password: str) -> str:
    """
    返回用户id
    :param username: 智学网用户名
    :param password: 智学网密码
    :return:
        成功则返回session和user_id
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    data = session.post(TEST_PASSWORD_URL, data={
        "loginName": user_name,
        "password": password,
        "code": ""
    }).json()
    if data.get("data"):
        return data["data"]
    elif data["result"] != "success":
        raise UserOrPassError()
    return None


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


def Zhixuewang(user_name: str = None, password: str = None, user_id: str = None) -> User:
    """
    通过(用户id, 密码)或(用户名, 密码)登录智学网
    :param user_name: 用户名
    :param password: 密码
    :param user_id: 用户id
    :return 

    """
    if not (password and any([user_name, user_id])):
        raise ArgError("请检查参数.")
    if user_name:
        user_id = get_user_id(user_name, password)
    session = login_id(user_id, password)
    roles = get_roles(session, user_id)
    if "headteacher" in roles:
        user = Headteacher(session)
    elif "headmaster" in roles:
        user = Headmaster(session)
    elif "teacher" in roles:
        user = Teacher(session)
    elif "student" in roles:
        user = Student(session)
    else:
        raise Exception("账号是未知用户")
    if not user._get_info():
        raise UserDefunctError("帐号已失效")
    return user


def get_user_info_by_user_name(url, user_name: str) -> str:
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
        r = requests.post(f"{url}/b", files={
            'image_file': ('captcha.png', open("captcha.png", "rb"), 'application')
        })
        return r.json()["value"]

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
        "a": user_name,
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
