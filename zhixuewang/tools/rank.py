from typing import Dict, List


def get_rank_map(data: List[float]) -> Dict[float, int]:
    last = 0
    rankMap: Dict[float, int] = {}
    i = 0
    for cur in data:
        if abs(last - cur) > 1e-10:
            last = cur
            rankMap[cur] = i + 1
        i += 1
    return rankMap