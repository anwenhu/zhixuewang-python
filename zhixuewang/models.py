from collections import namedtuple

class scoreDataModel(namedtuple("scoreDataModel", [
        "score",
        "classRank",
        "gradeRank",
        "subjectName",
        "standardScore",
        "examName",
        "examId",
    ])):
    def __str__(self):
        return f"{self.subjectName}:\n分数: {self.score}\n{str(self.classRank)}\n{str(self.gradeRank)}"

class classDataModel(namedtuple("classDataModel", [
        "avgScore",
        "highScore",
        "rank",
        "lowScore"
    ])):
    def __str__(self):
        return f"班级平均分: {self.avgScore}\n班级最高分: {self.highScore}\n班级最低分: {self.lowScore}\n班级排名: {self.rank}"

class gradeDataModel(namedtuple("gradeDataModel", [
        "avgScore",
        "highScore",
        "lowScore"
    ])):
    def __str__(self):
        return f"年级平均分: {self.avgScore}\n年级最高分: {self.highScore}\n年级最低分: {self.lowScore}"

examDataModel = namedtuple("examDataModel", [
    "examId",
    "examName",
])

