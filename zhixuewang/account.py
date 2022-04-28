from dataclasses import dataclass
import json
from zhixuewang.exceptions import LoginError
from zhixuewang.models import Role
import pickle
from zhixuewang.tools.cookies import get_tgt_from_session
from zhixuewang.tools.session import get_basic_session
from zhixuewang.urls import Url

@dataclass
class AccountData:
    tgt: str
    role: Role

class Account:
    def __init__(self, session, role: Role) -> None:
        self._session = session
        self.role = role

    def save_account(self, path: str = "user.data"):
        with open(path, "wb") as f:
            pickle.dump(AccountData(get_tgt_from_session(self._session), self.role), f)
    

    def update_login_status(self):
        """更新登录状态. 如果session过期自动重新获取"""
        r = self._session.get(Url.GET_LOGIN_STATE)
        data = r.json()
        if data["result"] == "success":
            return
        # session过期
        self._session = get_session_tgt(get_tgt_from_session(self._session))


def get_session_tgt(tgt: str):
    session = get_basic_session()
    session.cookies.set("CASTGC", tgt, domain="open.changyan.com")
    r = session.get(Url.SSO_URL)
    json_obj = json.loads(r.text.strip().replace("\\", "").replace("'", "")[1:-1])
    if json_obj["code"] != 1001:
        print(r.text)
        raise LoginError("tgt 已失效")
    r = session.post(Url.SERVICE_URL, data={
        "action": "login",
        "ticket": json_obj["data"]["st"],
    })
    return session



