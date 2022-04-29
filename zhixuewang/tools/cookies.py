from zhixuewang.tools.password_helper import base64_decode


def get_password_from_session(session):
    return base64_decode(session.cookies["pwd"])

def get_username_from_session(session):
    return base64_decode(session.cookies["uname"])