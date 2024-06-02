import base64
import pickle

from zhixuewang.exceptions import RoleError
from zhixuewang.models import Account, AccountData, Role
from zhixuewang.session import check_is_student, get_session, get_session_id, get_basic_session
from zhixuewang.student.student import StudentAccount
from zhixuewang.teacher.teacher import TeacherAccount


def load_account(path: str = "user.data") -> Account:
    with open(path, "rb") as f:
        data = base64.b64decode(f.read())
        account_data: AccountData = pickle.loads(data)
        session = get_session(account_data.username, account_data.encoded_password)
        if account_data.role == Role.student:
            return StudentAccount(session).set_base_info()
        elif account_data.role == Role.teacher:
            return TeacherAccount(session).set_base_info()
        else:
            raise RoleError()


def login_student_id(user_id: str, password: str) -> StudentAccount:
    """通过用户id和密码登录学生账号

    Args:
        user_id (str): 用户id
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        StudentAccount
    """
    session = get_session_id(user_id, password)
    student = StudentAccount(session)
    return student.set_base_info()

def login_cookie(cookies: dict) -> StudentAccount:
    """通过cookie登录账号

    Args:
        cookie (dict): 用户cookie

    Returns:
        Person
    """
    session = get_basic_session()

    # 更新会话的cookie
    session.cookies.update(cookies)
    session.cookies.set("uname", base64.b64encode(cookies["loginUserName"].encode()).decode())

    if check_is_student(session):
        return StudentAccount(session).set_base_info()
    return TeacherAccount(session).set_base_info().set_advanced_info()


def login_student(username: str, password: str) -> StudentAccount:
    """通过用户名和密码登录学生账号

    Args:
        username (str): 用户名, 可以为准考证号, 手机号
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        StudentAccount
    """
    session = get_session(username, password)
    student = StudentAccount(session)
    return student.set_base_info()


def login_teacher_id(user_id: str, password: str) -> TeacherAccount:
    """通过用户id和密码登录老师账号

    Args:
        user_id (str): 用户id
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        TeacherAccount
    """
    session = get_session_id(user_id, password)
    teacher = TeacherAccount(session)
    return teacher.set_base_info().set_advanced_info()


def login_teacher(username: str, password: str) -> TeacherAccount:
    """通过用户名和密码登录老师账号

    Args:
        username (str): 用户名, 可以为准考证号, 手机号
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误

    Returns:
        TeacherAccount
    """
    session = get_session(username, password)
    teacher = TeacherAccount(session)
    return teacher.set_base_info().set_advanced_info()


def login_id(user_id: str, password: str) -> Account:
    """通过用户id和密码登录智学网

    Args:
        user_id (str): 用户id
        password (str): 密码(包括加密后的密码)

    Raises:
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误
        RoleError: 账号角色未知

    Returns:
        Person
    """
    session = get_session_id(user_id, password)
    if check_is_student(session):
        return StudentAccount(session).set_base_info()
    return TeacherAccount(session).set_base_info()


def login(username: str, password: str) -> Account:
    """通过用户名和密码登录智学网

    Args:
        username (str): 用户名, 可以为准考证号, 手机号
        password (str): 密码(包括加密后的密码)

    Raises:
        ArgError: 参数错误
        UserOrPassError: 用户名或密码错误
        UserNotFoundError: 未找到用户
        LoginError: 登录错误
        RoleError: 账号角色未知

    Returns:
        Person
    """
    session = get_session(username, password)
    if check_is_student(session):
        return StudentAccount(session).set_base_info()
    return TeacherAccount(session).set_base_info().set_advanced_info()


def rewrite_str(model):
    """重写类的__str__方法

    Args:
        model: 需重写__str__方法的类

    Examples:
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
