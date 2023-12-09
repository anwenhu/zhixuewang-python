import json
import requests
from zhixuewang.exceptions import LoginError, UserNotFoundError, UserOrPassError
import base64
from zhixuewang.urls import Url


def get_basic_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    return session


def get_session(username: str, password: str, _type: str = "auto") -> requests.Session:
    """通过用户名和密码获取session

    默认可支持zx, zxt和tch开头的账号, 准考证号以及手机号
    可通过改变type为id来支持使用用户id

    Args:
        username (str): 用户名, 可以为准考证号, 手机号, id
        password (str): 密码(包括加密后的密码)
        _type (str): 登录方式, 为id时表示用id登录, 为auto时表示自动选择登录方式

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        requests.session:
    """
    if len(password) != 32:
        password = (
            pow(
                int.from_bytes(password.encode()[::-1], "big"),
                65537,
                186198350384465244738867467156319743461,
            )
            .to_bytes(16, "big")
            .hex()
        )  # by immoses648
    session = get_basic_session()
    r = session.get(Url.SSO_URL, proxies={'https': None, 'http': None})

    json_obj = json.loads(r.text.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1000:
        raise LoginError(json_obj["data"])
    lt = json_obj["data"]["lt"]
    execution = json_obj["data"]["execution"]
    r = session.get(
        Url.SSO_URL,
        params={
            "encode": "true",
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
            "password": password,
        },
    )
    json_obj = json.loads(r.text.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1001:
        if json_obj["code"] == 1002:
            raise UserOrPassError()
        if json_obj["code"] == 2009:
            raise UserNotFoundError()
        raise LoginError(json_obj["data"])
    ticket = json_obj["data"]["st"]
    session.post(
        Url.SERVICE_URL,
        data={
            "action": "login",
            "ticket": ticket,
        },
    )
    session.cookies.set("uname", base64.b64encode(username.encode()).decode())
    session.cookies.set("pwd", base64.b64encode(password.encode()).decode())
    return session


def get_session_id(user_id: str, password: str) -> requests.Session:
    """通过用户id和密码获取session

    Args:
        user_id (str): 用户id
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        requests.session:
    """
    return get_session(user_id, password, "id")


def get_user_id(username: str, password: str) -> str:
    """返回用户id

    Args:
        username (str): 用户名, 可以为准考证号, 手机号
        password (str): 密码

    Raises:
        UserOrPassError: 用户名或密码错误

    Returns:
        str: 用户id
    """
    session = requests.Session()
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    r = session.post(
        Url.TEST_PASSWORD_URL,
        data={"loginName": username, "password": password, "code": ""},
    )
    json_obj = r.json()  # {"data": ErrorMsg, "result": StatusCode}
    if json_obj.get("data"):
        return json_obj["data"]
    if json_obj["result"] != "success":
        raise UserOrPassError()
    return ""


def check_is_student(s: requests.Session) -> bool:
    """判断用户是否为学生

    Args:
        s (requests.session): session

    Returns:
        bool:
    """
    url = s.get("https://www.zhixue.com/container/container/index/").url
    return "student" in url
