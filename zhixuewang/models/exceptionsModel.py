class Error(Exception):
    pass


class LoginError(Error):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class UserOrPassError(Error):
    def __init__(self, value=None):
        self.value = value or "用户名或密码错误!"

    def __str__(self):
        return str(self.value)

class UserNotFound(Error):
    def __init__(self, value=None):
        self.value = value or "用户不存在"
    
    def __str__(self):
        return str(self.value)

class UserDefunctError(Error):
    def __init__(self, value=None):
        self.value = value or "用户已失效!"

    def __str__(self):
        return str(self.value)


class ArgError(Error):
    def __init__(self, value=None):
        self.value = value or "请输入正确的参数!"

    def __str__(self):
        return str(self.value)

class NeedVaildName(Error):
    def __init__(self, value=None):
        self.value = value or "该用户需要验证姓名, 请使用Zhixuewang_vaild_name()登录"
    
    def __str__(self):
        return str(self.value)
