import uuid
import inspect


def is_valid_uuid(msg: str):
    """判断msg是否为uuid"""
    try:
        uuid_obj = uuid.UUID(msg)
    except ValueError:
        return False
    return str(uuid_obj) == msg


def get_current_function_name():
    return inspect.currentframe().f_back.f_code.co_name
