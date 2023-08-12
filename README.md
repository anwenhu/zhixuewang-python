# zhixuewang-python

![](https://img.shields.io/badge/License-MIT-blue) ![](https://img.shields.io/badge/Python-3+-green) ![](https://img.shields.io/pypi/v/zhixuewang)

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

### 简单示例
```python
from zhixuewang import login

zxw = login(您的智学网账号, 您的智学网密码)
print(zxw.get_self_mark())
```
运行这段代码后会输出如下结果(以下仅供参考)
```
您的名字-考试名称
语文: 121.0 (班级第2名)
数学: 121.0 (班级第21名)
英语: 137.5 (班级第5名)
理综: 277.0 (班级第3名)
物理: 101.0 (班级第12名)
化学: 93.0 (班级第1名)
生物: 83.0 (班级第14名)
总分: 656.5
```
**注: 获取班级名次仅获取最新一次考试成绩有效, 且此库无法获取您的校级名次**

我们的文档在：[文档](https://zxdoc.risconn.com)，更多高级功能均在那里介绍。


## 问题和建议
如果您在使用的过程中遇到任何问题，欢迎前往 [Issue](https://github.com/anwenhu/zhixuewang/issues)提问
当然也可以加入这个QQ群讨论：862767072（备注：智学网）
如果有其它不常见的功能需求, 可以前往MasterYuan418大佬的[zxext](https://github.com/MasterYuan418/zxext)查找或提出