import asyncio
import base64
from typing import Union

import requests
from playwright.async_api import Playwright, async_playwright

from zhixuewang.models import Account
from zhixuewang.session import get_basic_session
from zhixuewang.student.student import StudentAccount
from zhixuewang.teacher.teacher import TeacherAccount


def check_is_student(s: requests.Session) -> bool:
    """判断用户是否为学生

    Args:
        s (requests.session): session

    Returns:
        bool:
    """
    url = s.get("https://www.zhixue.com/container/container/index/").url
    return "student" in url



def login_cookie(cookies: Union[dict, str]) -> Account:
    """通过cookie登录账号

    Args:
        cookies (Union[dict, str]): 用户cookie

    Returns:
        Person
    """
    session = get_basic_session()

    # 更新会话的cookie
    if isinstance(cookies, str):
        cookies = dict(item.split("=") for item in cookies.split("; "))
    session.cookies.update(cookies)
    session.cookies.set("uname", base64.b64encode(cookies["loginUserName"].encode()).decode())

    if check_is_student(session):
        return StudentAccount(session).set_base_info()
    return TeacherAccount(session).set_base_info().set_advanced_info()

async def playwright_get_cookie(playwright: Playwright, username: str, password: str) -> dict:
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.zhixue.com/wap_login.html")
    await page.wait_for_load_state('networkidle')  # 等待网络状态为空闲
    print(await page.title())
    await page.fill('#txtUserName', username)
    await page.fill('#txtPassword', password)

    # 点击注册按钮
    await asyncio.sleep(0.5)
    await page.click('#signup_button')
    await page.wait_for_url("https://www.zhixue.com/htm-vessel/**", timeout=float('inf'))
    cookies = await page.context.cookies()
    # 将Cookie转换为字典
    cookies_dict = {cookie.get("name"): cookie.get("value") for cookie in cookies}
    await browser.close()
    return cookies_dict

async def playwright_process(username: str, password: str):
    async with async_playwright() as playwright:
        return await playwright_get_cookie(playwright, username, password)

def login_playwright(username: str, password: str)  -> Account:
    """通过playwright更加便利的登录账号

    Args:
        username (str): 用户名, 可以为准考证号, 手机号
        password (str): 密码

    Returns:
        Person
    """
    session = get_basic_session()

    # 更新会话的cookie
    cookies = asyncio.run(playwright_process(username, password))
    session.cookies.update(cookies)
    session.cookies.set("uname", base64.b64encode(cookies["loginUserName"].encode()).decode())

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
