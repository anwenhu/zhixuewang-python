class Error(Exception):
    pass


class UserOrPassError(Error):
    def __init__(self, value=None):
        self.value = value or "用户名或密码错误!"

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
