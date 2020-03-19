import json
import requests
from zhixuewang.exceptions import ArgError, UserNotFoundError, UserOrPassError, LoginError
from zhixuewang.urls import Url
from zhixuewang.models import Person
from zhixuewang.student import Student
from zhixuewang.teacher import Teacher, Headmaster, Headteacher


def get_session(username: str, password: str,
                _type: str = "auto") -> requests.session:
    """通过用户名和密码获取session

    默认可支持zx和zxt开头的账号, 准考证号以及手机号
    可通过改变type为id来支持使用用户id

    参数
    --------------------
    username: str
        用户名, 可以为准考证号, 手机号, id
    password: str
        密码
    key: str
        登录方式
        id 表示用id登录
        auto 表示自动选择登录方式

    返回值
    --------------------
    requests.session
    """
    session = requests.Session()
    session.headers[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    r = session.get(Url.SSO_URL)
    msg = r.text
    json_obj = json.loads(msg.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1000:
        raise LoginError(json_obj["data"])
    lt = json_obj["data"]["lt"]
    execution = json_obj["data"]["execution"]
    r = session.get(Url.SSO_URL,
                    params={
                        "encode": "false",
                        "sourceappname": "tkyh,tkyh",
                        "_eventId": "submit",
                        "appid": "zx-container-client",
                        "client": "web",
                        "type": "loginByNormal",
                        "key": _type,
                        "lt": lt,
                        "execution": execution,
                        "customLogoutUrl": "https://www.zhixue.com/login.html",
                        "username": username,
                        "password": password
                    })
    msg = r.text
    json_obj = json.loads(msg.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1001:
        if json_obj["code"] == 1002:
            raise UserOrPassError()
        if json_obj["code"] == 2009:
            raise UserNotFoundError()
        raise LoginError(json_obj["data"])
    ticket = json_obj["data"]["st"]
    session.post(Url.SERVICE_URL, data={
        "action": "login",
        "ticket": ticket,
    })
    return session


def get_session_id(user_id: str, password: str) -> requests.session:
    """通过用户id和密码获取session

    参数
    --------------------
    user_id: str
        id
    password: str
        密码

    返回值
    --------------------
    requests.session
    """
    return get_session(user_id, password, "id")


def get_user_id(username: str, password: str) -> str:
    """返回用户id

    参数
    --------------------
    user_id: str
        用户名, 可以为准考证号, 手机号
    password: str
        密码

    返回值
    --------------------
    str
        用户id
    """
    session = requests.Session()
    session.headers[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    r = session.post(Url.TEST_PASSWORD_URL,
                     data={
                         "loginName": username,
                         "password": password,
                         "code": ""
                     })
    json_obj = r.json()  # {"data": ErrorMsg, "result": StatusCode}
    if json_obj.get("data"):
        return json_obj["data"]
    if json_obj["result"] != "success":
        raise UserOrPassError()
    return ""


def check_is_student(s: requests.session) -> bool:
    """判断用户是否为学生

    参数
    --------------------
    s: requests.session

    返回值
    --------------------
    bool
    """
    url = s.get("https://www.zhixue.com/container/container/index/").url
    return "student" in url


def login_student_id(user_id: str, password: str) -> Student:
    """通过用户id和密码登录学生账号

    参数
    --------------------
    user_id: str
        用户id
    password: str
        密码

    返回值
    --------------------
    Student
    """
    session = get_session_id(user_id, password)
    student = Student(session)
    return student.set_base_info()


def login_student(username: str, password: str) -> Student:
    """通过用户名和密码登录学生账号

    参数
    --------------------
    username: str
        用户名, 可以为准考证号, 手机号
    password: str
        密码

    返回值
    --------------------
    Student
    """
    session = get_session(username, password)
    student = Student(session)
    return student.set_base_info()


def login_teacher_id(user_id: str, password: str) -> Teacher:
    """通过用户id和密码登录老师账号

    参数
    --------------------
    user_id: str
        用户id
    password: str
        密码

    返回值
    --------------------
    Teacher
    """
    session = get_session_id(user_id, password)
    teacher = Teacher(session)
    return teacher.set_base_info()


def login_teacher(username: str, password: str) -> Teacher:
    """通过用户名和密码登录老师账号

    参数
    --------------------
    username: str
        用户名, 可以为准考证号, 手机号
    password: str
        密码

    返回值
    --------------------
    Teacher
    """
    session = get_session(username, password)
    teacher = Teacher(session)
    return teacher.set_base_info()


def login(username: str = None, password: str = None,
          user_id: str = None) -> Person:
    """通过(用户id, 密码)或(用户名, 密码)登录智学网

    参数
    --------------------
    username: str
        用户名, 可以为准考证号, 手机号
    password: str
        密码
    user_id: str
        用户id

    返回值
    --------------------
    Person
    """
    if not (password and any([username, user_id])):
        raise ArgError("请检查参数")
    if username:
        session = get_session(username, password)
    else:
        session = get_session_id(user_id, password)
    if check_is_student(session):
        return Student(session).set_base_info()
    teacher = Teacher(session).set_base_info()
    if teacher.role == "headteacher":
        teacher = Headteacher(teacher)
    elif teacher.role == "headmaster":
        teacher = Headmaster(teacher)
    else:
        raise Exception("账号是未知用户")
    return teacher.set_base_info()


def rewrite_str(model):
    """重写类的__str__方法

    参数
    --------------------
    model:
        需重写__str__方法的类

    示例
    --------------------
    >>> from zhixuewang.models import School

    >>> @rewrite_str(School)
    >>> def _(self: School):
    >>>     return f"<id: {self.id}, name: {self.name}>"

    >>> print(School("test id", "test school"))
    <id: test id, name: test school>
    """
    def str_decorator(func):
        model.__str__ = func
        return func

    return str_decorator
