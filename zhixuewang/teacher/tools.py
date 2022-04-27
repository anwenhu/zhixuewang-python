from zhixuewang.models import ExtendedList, SubjectScore
from typing import Callable, TypeVar
T = TypeVar("T")
def order_by(data: ExtendedList[T], f: Callable[[T], str]):
    classIdMap = {}
    for each in data:
        idno = f(each)
        if idno not in classIdMap:
            classIdMap[idno] = []
        classIdMap[idno].append(each)
    return classIdMap



def order_by_classId(subjectScores: ExtendedList[SubjectScore]):
    return order_by(subjectScores, lambda t: t.person.clazz.id)


def order_by_schoolId(subjectScores: ExtendedList[SubjectScore]):
    return order_by(subjectScores, lambda t: t.person.clazz.school.id)
