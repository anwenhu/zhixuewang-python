# 智学网

## 安装:
```bash
pip3 install zhixuewang
```
或
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
python setup.py install
```


## 使用
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
grades = zxw.get_self_mark(考试名字)
print(grades)
```
### 获取最新考试某一学科的原卷url(不含打分情况)
```python
urls = zxw.get_original(学科)
print(urls)
```
### 获取指定考试某一学科的原卷url(不含打分情况)
```python
urls = zxw.get_original(学科, 考试名字)
print(urls)
```
其余函数的使用方法请自行查看源码说明.
## 问题和建议
如果有什么问题或者建议都可以在这个[Issue](https://github.com/anwenhu/zhixuewang/issues)和我讨论
当然也可以加入这个新建的QQ群讨论：862767072
