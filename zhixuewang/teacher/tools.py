import math
from zhixuewang.models import ExtendedList, Subject, SubjectScore
from typing import Callable, Dict, List, TypeVar
import numpy

from zhixuewang.teacher.models import ExtraData, RankData
from zhixuewang.tools.rank import get_rank_map
T = TypeVar("T")

V = TypeVar("V")

# 52 10 : 0-9 10-19 20-29 30-39 40-49 50-59
# 13 3: 0-2 3-5 
def divide_array(array: List[T], count: int) -> List[List[T]]:
    result = []
    for i in range(math.ceil(len(array) / count)):
        result.append(array[i*count:i*count + count])
    return result

def group_by(data: List[T], f: Callable[[T], V]) -> Dict[V, List[T]]:
    data_map: Dict[V, List[T]] = {}
    for each in data:
        v = f(each)
        if v not in data_map:
            data_map[v] = [each]
        else:
            data_map[v].append(each)
    return data_map

def group_by_school_id(subjectScores: List[SubjectScore]) -> Dict[str, List[SubjectScore]]:
    return group_by(subjectScores, lambda t: t.person.clazz.school.id)

def group_by_class_id(subjectScores: List[SubjectScore]) -> Dict[str, List[SubjectScore]]:
    return group_by(subjectScores, lambda t: t.person.clazz.id)

def spread_array(array: List[List[T]]) -> List[T]:
    new_array = []
    for array2 in array:
        new_array.extend(array2)
    return new_array

def get_rank_data(subjectScores: ExtendedList[SubjectScore]):
    schoolIdMap = group_by_school_id(subjectScores)
    rankData = RankData(dict(), dict(), dict())
    all_rankMap = get_rank_map([i.score for i in subjectScores])
    if len(schoolIdMap.keys()) == 1:
        # 单校
        rankData.schoolRankMap["all"] = all_rankMap
        classIdMap = group_by_class_id(subjectScores)
        for classId, _subjectScores in classIdMap.items():
            rankData.schoolRankMap[classId] = get_rank_map([i.score for i in _subjectScores])
        return rankData, False
    else:
        # 多校
        rankData.allRankMap = all_rankMap
        for schoolId, schoolSubjectScores in schoolIdMap.items():
            school_all_rankMap = get_rank_map(
                [i.score for i in schoolSubjectScores])
            rankData.schoolsRankMap[schoolId] = {}
            rankData.schoolsRankMap[schoolId]["all"] = school_all_rankMap
            classIdMap = group_by_class_id(schoolSubjectScores)
            for classId, classSubjectScores in classIdMap.items():
                rankData.schoolsRankMap[schoolId][classId] = get_rank_map([i.score for i in classSubjectScores])
        return rankData, True


def set_rank(subjectScores: ExtendedList[SubjectScore]):
    subjectScores.sort(key=lambda t: t.score, reverse=True)
    extraData, has_many_schools = get_rank_data(subjectScores)
    for each in subjectScores:
        class_id = each.person.clazz.id
        school_id = each.person.clazz.school.id
        score = each.score
        try:
            if has_many_schools:
                each.class_rank = extraData.schoolsRankMap[school_id][class_id][score]
                each.grade_rank = extraData.schoolsRankMap[school_id]["all"][score]
                each.exam_rank = extraData.allRankMap[score]
            else:
                each.class_rank = extraData.schoolRankMap[class_id][score]
                each.grade_rank = extraData.schoolRankMap["all"][score]
        except Exception as e:
            print(extraData.schoolsRankMap[school_id])
            print(extraData.schoolsRankMap[school_id][class_id])
            print("")
            print(extraData.schoolsRankMap[school_id]["all"])
            raise e


def calc_total_score(data) -> ExtendedList[SubjectScore]:
    # personScoreMap = group_by(data, lambda t: )
    personScoreMap = group_by(spread_array(data), lambda t: t.person.id)
    totalScores: ExtendedList[SubjectScore] = ExtendedList()
    for personSubjectScores in personScoreMap.values():
        totalSubjectScore = SubjectScore(
            score=0,
            subject=Subject(name="总分", standard_score=0),
            person=personSubjectScores[0].person
        )
        for each in personSubjectScores:
            totalSubjectScore.score += each.score
            totalSubjectScore.subject.standard_score += each.subject.standard_score
        totalScores.append(totalSubjectScore)
    totalScores = ExtendedList(
        sorted(totalScores, key=lambda t: t.score, reverse=True))
    return totalScores

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
