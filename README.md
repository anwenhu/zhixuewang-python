# zhixuewang-python

**注意: 由于登录接口变动, 如果只有学生账号, 该项目与智学网网页版并无二致, 此项目将大概率不会再有关于接口的更新**

![](https://img.shields.io/badge/License-MIT-blue) ![](https://img.shields.io/badge/Python-3+-green) ![](https://img.shields.io/pypi/v/zhixuewang)

## 安装

### 使用 pip 安装（推荐）
```bash
pip install zhixuewang
```
### 下载 源码 安装
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
python setup.py install
```



## 简单示例
### playwright登录（python3.7+）
#### 安装依赖
```
pip install playwright
playwright install chromium
```
#### python代码
```python
from zhixuewang.account import login_playwright

zxw = login_playwright(您的智学网账号, 您的智学网密码)
# 然后通过浏览器完成人机验证

print(zxw.get_self_mark())
```
### 你也可以手动获取cookie登录
#### python代码
```python
# from zhixuewang import login_cookie
from zhixuewang.account import login_cookie

# zxw = login(您的智学网账号, 您的智学网密码)
# 因为智学网接口变动暂时失效，请先使用cookie登录方式
# 复制的cookie字符串
cookie_string = "xxx"

# 将cookie字符串转换为字典
cookies = dict(item.split("=") for item in cookie_string.split("; "))
zxw = login_cookie(cookies)

print(zxw.get_self_mark())
```
#### cookie可以在登录智学网网页端后用以下js书签获取
```javascript
javascript:(function(){function getCookies(){return document.cookie;}function copyToClipboard(text){const textarea=document.createElement('textarea');textarea.value=text;document.body.appendChild(textarea);textarea.select();document.execCommand('copy');document.body.removeChild(textarea);}const cookies=getCookies();copyToClipboard(cookies);alert('Cookies 已复制到剪切板！');})();
```
### 结果（仅供参考）
```
您的名字-考试名称
语文: 121.0
数学: 121.0
英语: 137.5
理综: 277.0
物理: 101.0
化学: 93.0
生物: 83.0
总分: 656.5
```

**更多高级功能请[查看文档](https://zxdoc.risconn.com)。**



## 问题和建议

如果您在使用的过程中遇到任何问题，或是有任何建议：

① 加入QQ群进行讨论：862767072（备注：**GitHub智学网库**）；

② 前往 [Issues](https://github.com/anwenhu/zhixuewang/issues) 进行提问；

③ 如果您想直接贡献代码，欢迎直接 [Pull requests](https://github.com/anwenhu/zhixuewang-python/pulls)。

如果有其它不常见的功能需求, 可以前往 [MasterYuan418/zxext](https://github.com/MasterYuan418/zxext) 查找或提出。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=anwenhu/zhixuewang-python&type=Date)](https://star-history.com/#anwenhu/zhixuewang-python&Date)
