import requests


def get_basic_session() -> requests.Session:
    session = requests.Session()
    session.headers[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
    return session