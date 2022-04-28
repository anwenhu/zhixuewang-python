import pickle
from zhixuewang.account import Account, AccountData, get_session_tgt
from zhixuewang.exceptions import RoleError
from zhixuewang.models import Role
from zhixuewang.student.student import StudentAccount
from zhixuewang.teacher.teacher import TeacherAccount


def load_account(path: str = "user.data") -> Account:
    with open(path, "rb") as f:
        account_data: AccountData = pickle.load(f)
        session = get_session_tgt(account_data.tgt)
        if account_data.role == Role.student:
            return StudentAccount(session).set_base_info()
        elif account_data.role == Role.teacher:
            return TeacherAccount(session).set_base_info()
        else:
            raise RoleError()

