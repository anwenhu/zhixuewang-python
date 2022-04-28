from zhixuewang.models import ExtendedList, SubjectScore
from typing import Callable, Dict, List, TypeVar
import numpy

from zhixuewang.teacher.models import ExtraData
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

V = TypeVar("V")
def group_by(data: List[T], f: Callable[[T], V]) -> Dict[V, List[T]]:
    data_map: Dict[V, List[T]] = {}
    for each in data:
        v = f(each)
        if v not in data_map:
            data_map[v] = [each]
        else:
            data_map[v].append(each)
    return data_map

def get_extra_data(scores: List[SubjectScore], standard_score: float) -> ExtraData:
    raw_scores = [i.score for i in scores]
    arr = numpy.array(raw_scores)
    avg_score = numpy.mean(arr)
    medium_score = numpy.median(arr)
    pass_number = len(arr[arr >= 0.6 * standard_score])
    excellent_number = len(arr[arr >= 0.85 * standard_score])
    perfect_number = len(arr[abs(arr - standard_score) < 1e-5])
    all_number = len(scores)
    var = numpy.var(arr)
    return ExtraData( 
        avg_score,
        medium_score,
        pass_number / all_number,
        excellent_number / all_number,
        perfect_number / all_number,
        var
    )