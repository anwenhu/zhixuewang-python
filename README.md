# 智学网

## 安装:
```bash
pip install zhixuewang
```

或
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
python setup.py install
```


## 使用
```python
from zhixuewang import Zhixuewang
zxw = Zhixuewang(user, password)
grades = zxw.get_self_grade()
for grade in grades:
    print(grade.score)
    print(grade.classRank.rank)
```
