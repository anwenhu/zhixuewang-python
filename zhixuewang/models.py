from collections import namedtuple

subjectDataModel = namedtuple("scoreDataModel", [
    "score",
    "classRank",
    "gradeRank",
    "subjectName",
    "standardScore",
    "examName",
    "examId"
])
classDataModel = namedtuple("classDataModel", [
    "avgScore",
    "highScore",
    "rank",
    "lowScore"
])
gradeDataModel = namedtuple("gradeDataModel", [
    "avgScore",
    "highScore",
    "lowScore"
])

examDataModel = namedtuple("examDataModel", [
    "examId",
    "examName",
])
