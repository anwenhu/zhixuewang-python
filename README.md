# zhixuewang-python

## 安装:

### 使用 pip 安装(推荐)
```bash
pip install zhixuewang
```
### 下载 源码 安装
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
python setup.py install
```


## 快速使用
### 登录:
保证你已经安装好zhixuewang后, 通过这样来获取自己最新一次考试成绩并打印到屏幕上

```python
from zhixuewang import login
username = input("你的用户名:").strip()
password = input("你的密码:").strip()
zxw = login(username, password)
print(zxw.get_self_mark())
```
在输入智学网用户名和密码后, 屏幕上会显示形如::
```python
name 语文:
分数: 105
name 数学:
分数: 120
name 英语:
分数: 132
name 物理:
分数: 68
name 化学:
分数: 52
name 政治:
分数: 49
name 历史:
分数: 59
name 总分:
分数: 585

其中 `name` 的位置应该显示你的名字

如果你想要查询指定考试的成绩, 如查询"某中学第二次月考", 可这样做(假定你已经运行了前面的代码)::
```python
print(zxw.get_self_mark("某中学第二次月考"))
```
(注: 因为智学网移除了部分接口, 所以查询班级平均分, 班级最高分等功能暂时失效)

具体的还可查看[Wiki](https://zhixuewang-python.readthedocs.io/zh_CN/latest/)~(不过Wiki正在制作中，如果愿意帮忙维护的话，可以加我QQ: 1223009522 备注github wiki)~

## 问题和建议
如果您在使用的过程中遇到任何问题，欢迎前往 [Issue](https://github.com/anwenhu/zhixuewang/issues)提问
当然也可以加入这个QQ群讨论：862767072