import datetime
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QCompleter,
    QTableWidgetItem,
    QMainWindow,
)
from openpyxl import Workbook
from zhixuewang import login as login_zhixuewang
from zhixuewang.models import Exam, ExtendedList
from PySide6.QtCore import Slot, QObject, Signal
from PySide6.QtGui import QTextCursor
from ui_login import Ui_Dialog
from ui_mainWindow import Ui_MainWindow
import pandas as pd
from dataclasses import dataclass
import os
import traceback

cur_dir = os.path.dirname(__file__)  # os.path.abspath


def get_path(relative_path: str):
    return os.path.abspath(os.path.join(cur_dir, relative_path))


USER_FILE = get_path("./user")
TOKEN_FILE = get_path("token.txt") # 打包时需要修改为../token.txt
with open(TOKEN_FILE) as f:
    token = f.readlines()[0].strip()  # 可修改为你自己的token


def export_to_xlsx(data, name, subject_codes):
    wb = Workbook()
    sheet = wb.active
    column_names = [
        "姓名",
        "用户id",
        "用户code(准考证号)",
        "班级",
        "班级id",
        "学校",
        "学校id",
        "总分",
        "总分班排",
        "总分年排",
        "总分总排",
    ]
    subjects = sorted(data[0]["eachSubjectScore"], key=lambda x: x["subjectCode"])
    sheet.append(
        column_names
        + [
            i
            for each in subjects
            for i in [
                each["subjectName"],
                each["subjectName"] + "班排",
                each["subjectName"] + "年排",
                each["subjectName"] + "总排",
            ]
        ]
    )
    for each in data:
        added_data = [
            each["userName"],
            each["userId"],
            each["userCode"],
            each["className"],
            each["classId"],
            each["schoolName"],
            each["schoolId"],
            each["totalScore"],
            each["classRank"],
            each["schoolRank"],
            each["allRank"],
        ]
        for subject_code in subject_codes:
            added_data.extend(
                [
                    each[f"subject{subject_code}score"],
                    each[f"subject{subject_code}classRank"],
                    each[f"subject{subject_code}schoolRank"],
                    each[f"subject{subject_code}allRank"],
                ]
            )
        sheet.append(added_data)
    wb.save(name)


@dataclass
class Account:
    username: str
    password: str


def get_page_exams(zxw, page):
    r = zxw._session.get(
        f"https://www.zhixue.com/zxbReport/report/getPageAllExamList?pageIndex={page}&actualPosition=0&pageSize=10&reportType=exam&token="
        + zxw.get_auth_header()["XToken"]
    )
    result = r.json()["result"]
    if not result:
        return []
    exams = []
    for each in result["examInfoList"]:
        exams.append(
            Exam(
                id=each["examId"],
                name=each["examName"],
                create_time=each["examCreateDateTime"],
            )
        )
    return ExtendedList(exams)


def get_exams(zxw):
    exams = ExtendedList()
    for page in range(1, 5 + 1):
        exams.extend(get_page_exams(zxw, page))
    return exams


class AccountHelper:
    def __init__(self) -> None:
        self.accounts = []

    def read_account(self):
        self.accounts = []
        if os.path.exists(USER_FILE):
            with open(USER_FILE, encoding="utf8") as f:
                for line in f.readlines():
                    if len(line) == 0 or "," not in line:
                        return
                    username, password = line.strip().split(",")
                    self.accounts.append(Account(username, password))

    def write_account(self):
        with open(USER_FILE, "w", encoding="utf8") as f:
            f.writelines(
                [
                    f"{account.username},{account.password}\n"
                    for account in self.accounts
                ]
            )

    def has_account(self, username):
        for account in self.accounts:
            if account.username == username:
                return True
        return False


class Login(QMainWindow):
    accountHelper: AccountHelper
    accountMap = {}

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        # 初始化界面
        self.ui.setupUi(self)
        # 自动补全账号
        self.accountHelper = AccountHelper()
        self.accountHelper.read_account()
        for account in self.accountHelper.accounts:
            self.accountMap[account.username] = account.password
        completer = QCompleter(self.accountMap.keys())
        self.ui.userEdit.setCompleter(completer)
        self.ui.userEdit.textChanged.connect(self.auto_input_pass)
        self.ui.button.clicked.connect(self.login_button)

    def auto_input_pass(self, text: str):
        if text in self.accountMap:
            self.ui.passEdit.setText(self.accountMap[text])
        else:
            self.ui.passEdit.setText("")

    def login_button(self):
        self.ui.button.setText("登录中...")
        username = self.ui.userEdit.text().strip()
        password = self.ui.passEdit.text().strip()
        QApplication.processEvents()
        try:
            zxw = login_zhixuewang(username, password)
            if username not in self.accountMap:
                self.accountHelper.accounts.append(
                    Account(username=username, password=password)
                )
                self.accountHelper.write_account()
            self.mainWindow = MainWindow(zxw)
            self.mainWindow.show()
            self.close()
        except Exception as e:
            QMessageBox.about(self, "登录错误", e.value)
            self.ui.button.setText("登录")
            self.ui.passEdit.clear()


@Slot(str)
class Stream(QObject):
    newText = Signal(str)

    def write(self, text):
        self.newText.emit(str(text))
        QApplication.processEvents()


def find(l: list, find_f, return_f, default):
    for i in l:
        if find_f(i):
            return return_f(i)
    return default


class MainWindow(QMainWindow):
    def __init__(self, zxw):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("智学网查成绩 v2.2.1 (by anwenhu) 特别感谢: YS")

        self.zxw = zxw

        self.list_exams()
        self.ui.searchButton.clicked.connect(self.download_score)

        sys.stdout = Stream(newText=self.onUpdateText)  # 将print重定向到框里

    def onUpdateText(self, text):
        cursor = self.ui.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.ui.textEdit.setTextCursor(cursor)
        self.ui.textEdit.ensureCursorVisible()

    def add_text(self, table, row, column, text):
        item = QTableWidgetItem()
        item.setText(text)
        table.setItem(row, column, item)

    def list_exams(self):
        table = self.ui.examTable
        self.exams = get_exams(self.zxw)
        table.setRowCount(len(self.exams))
        for i, exam in enumerate(self.exams):
            time = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(exam.create_time / 1000), "%Y-%m-%d"
            )
            self.add_text(table, i, 0, exam.id)
            self.add_text(table, i, 1, exam.name)
            self.add_text(table, i, 2, time)

    def download_score(self):
        items = self.ui.examTable.selectedItems()
        if len(items) == 0:
            self.ui.textEdit.setText("请选择考试")
        else:
            exam_id = self.ui.examTable.item(items[0].row(), 0).text()
            selected_exam = self.exams.find(lambda t: t.id == exam_id)
            print(f"正在下载{selected_exam.name}成绩... 操作会比较漫长\n")
            r = self.zxw._session.get(
                f"https://zhixuewfunction-serverllication-jpqeobvrff.cn-beijing.fcapp.run/getExamScore?examId={selected_exam.id}&token={token}"
            )
            if "token" in r.text:
                print("下载失败 请检查token是否正确...\n")
                return
            try:
                data = r.json()

                s = pd.DataFrame.from_dict(data["result"])
                s["totalScore"] = s.eachSubjectScore.apply(
                    lambda t: sum([each["score"] for each in t])
                )
                s["allRank"] = s.totalScore.rank(method="min", ascending=False)
                s.classRank = (
                    s.groupby("classId")
                    .totalScore.rank(method="min", ascending=False)
                    .astype(int)
                )
                s.schoolRank = (
                    s.groupby("schoolId")
                    .totalScore.rank(method="min", ascending=False)
                    .astype(int)
                )

                all_subject_code = [
                    set(map(lambda x: x["subjectCode"], each["eachSubjectScore"]))
                    for _, each in s.iterrows()
                ]
                subject_codes = sorted(
                    set(all_subject_code[0]).union(*all_subject_code[1:])
                )
                for subject_code in subject_codes:
                    s[f"subject{subject_code}score"] = s["eachSubjectScore"].apply(
                        lambda t: find(
                            t,
                            lambda each: each["subjectCode"] == subject_code,
                            lambda t: t["score"],
                            0,
                        )
                    )
                    s[f"subject{subject_code}allRank"] = s[
                        f"subject{subject_code}score"
                    ].rank(method="min", ascending=False)
                    s[f"subject{subject_code}classRank"] = (
                        s.groupby("classId")[f"subject{subject_code}score"]
                        .rank(method="min", ascending=False)
                        .astype(int)
                    )
                    s[f"subject{subject_code}schoolRank"] = (
                        s.groupby("schoolId")[f"subject{subject_code}score"]
                        .rank(method="min", ascending=False)
                        .astype(int)
                    )
                data = s.to_dict(orient="records")
                export_to_xlsx(data, f"考试成绩-{selected_exam.name}.xlsx", subject_codes)
                print("下载成功! 成绩已保存到程序所在目录下, 正在自动打开...")
                os.system(f"考试成绩-{selected_exam.name}.xlsx")
            except Exception:
                print("错误:\n")
                print(r.text)
                print(traceback.format_exc())


app = QApplication([])
login = Login()
login.show()

app.exec()
