import asyncio
import base64
from typing import Union

import requests
from playwright.async_api import Playwright, async_playwright

from zhixuewang.models import Account
from zhixuewang.parent.parent import ParentAccount
from zhixuewang.session import get_basic_session
from zhixuewang.student.student import StudentAccount
from zhixuewang.teacher.teacher import TeacherAccount


def get_account_role(s: requests.Session) -> str:
    r = s.get("https://www.zhixue.com/container/getCurrentUser")
    data = r.json()
    return data["result"]["role"]

def session_to_account(session: requests.Session) -> Account:
    """通过session获取账号对象

    Args:
        session (requests.Session): 用户session

    Returns:
        Account
    """
    role = get_account_role(session)
    if role == "student":
        return StudentAccount(session).set_base_info()
    elif role == "teacher":
        return TeacherAccount(session).set_base_info().set_advanced_info()
    elif role == "parent":
        return ParentAccount(session)
    else:
        return TeacherAccount(session).set_base_info().set_advanced_info()

def login_cookie(cookies: Union[dict, str]) -> Account:
    """通过cookie登录账号

    Args:
        cookies (Union[dict, str]): 用户cookie

    Returns:
        Account
    """
    session = get_basic_session()

    # 更新会话的cookie
    if isinstance(cookies, str):
        cookies = dict(item.split("=") for item in cookies.split("; "))
    session.cookies.update(cookies)
    session.cookies.set("uname", base64.b64encode(cookies["loginUserName"].encode()).decode())

    return session_to_account(session)

async def playwright_get_cookie(playwright: Playwright, username: str, password: str) -> dict:
    chromium = playwright.chromium
    
    browser = await chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='zh-CN',
        timezone_id='Asia/Shanghai',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' }
            ],
        });
        
        delete window.__playwright;
        delete window.__pw_manual;
    """)
    
    page = await context.new_page()
    await page.goto("https://www.zhixue.com/wap_login.html")
    await page.wait_for_load_state('networkidle')
    print(await page.title())
    await page.fill('#txtUserName', username)
    await page.fill('#txtPassword', password)

    # 点击登录按钮
    await asyncio.sleep(0.5)
    await page.click('#signup_button')
    
    # 等待跳转，超时时间保持无限（或设置一个合理值如 120000ms）
    await page.wait_for_url("https://www.zhixue.com/htm-vessel/**", timeout=float('inf'))
    
    cookies = await page.context.cookies()
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
        Account
    """
    session = get_basic_session()

    # 更新会话的cookie
    cookies = asyncio.run(playwright_process(username, password))
    session.cookies.update(cookies)
    session.cookies.set("uname", base64.b64encode(cookies["loginUserName"].encode()).decode())

    return session_to_account(session)

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
