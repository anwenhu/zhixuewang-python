# zhixuewang-python

## 安装:

### 使用 pip 安装(推荐)
```bash
pip3 install zhixuewang
```
### 下载 源码 安装
把项目源码下载后, 在项目根目录输入
```bash
python setup install
```
或直接
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
python setup.py install
```


## 快速使用
### 登录:
```python
from zhixuewang import Zhixuewang
zxw = Zhixuewang(你的用户名, 你的密码)
```
### 获取最新考试成绩
```python
grades = zxw.get_self_mark()
print(grades)
```
### 获取指定考试的考试成绩
```python
grades = zxw.get_self_mark(考试名字) # 形如 grades = zxw.get_self_mark("合肥13中九年级第一次月考") 
print(grades)
```
具体的还可查看[Wiki](https://github.com/anwenhu/zhixuewang/wiki/Home/)(不过Wiki正在制作中，如果愿意帮忙维护的话，可以加我QQ: 1223009522 备注github wiki)
## 问题和建议
如果您在使用的过程中遇到任何问题，欢迎前往 [Issue](https://github.com/anwenhu/zhixuewang/issues)提问
当然也可以加入这个新建的QQ群讨论：862767072
