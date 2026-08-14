# zhixuewang-python

**维护说明：由于智学网登录及部分接口发生变化，部分仅面向学生网页端的功能可能不再继续适配；项目仍会维护现有可用功能、兼容性问题、Bug 修复及社区贡献。**

![](https://img.shields.io/badge/License-MIT-blue) ![](https://img.shields.io/badge/Python-3+-green) ![](https://img.shields.io/pypi/v/zhixuewang)

`zhixuewang`是一个Python版的智学网API。它支持（包括但不限于）：查询分数，查看作业情况，查看阅卷情况等。

支持三种账号类型：
- **学生账号** - 查看考试成绩、作业、同学信息等
- **教师账号** - 查看考试、阅卷进度、下载原卷等
- **家长账号** - 查看孩子的考试成绩和作业（部分功能受限）

## 安装
本项目是基于`Python`的，所以你需要先安装`Python`环境。


### 前置条件

* Python 3.7及以上
* 手
  * 有手就行！

### 使用 pip 安装（推荐）

打开命令提示符（或bash），输入如下指令：

```bash
pip install zhixuewang
```

这将会自动安装本项目，待pip完成后安装便完成。

### 下载 源码 安装

打开命令提示符（或bash），输入如下指令：
```bash
git clone https://github.com/anwenhu/zhixuewang
cd zhixuewang
pip install .
```

## 简单示例
### playwright登录（python3.7+）
#### 安装依赖
```
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
from zhixuewang.account import login_cookie

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

**更多高级功能请[查看文档](https://anwenhu.github.io/zhixuewang-docs/)。**



## 问题和建议

如果您在使用的过程中遇到任何问题，或是有任何建议：

1. 加入QQ群进行讨论：862767072（备注：**GitHub智学网库**）；

2. 前往 [Issues](https://github.com/anwenhu/zhixuewang/issues) 进行提问；

3. 如果您想直接贡献代码，欢迎直接 [Pull requests](https://github.com/anwenhu/zhixuewang-python/pulls)。

如果有其它不常见的功能需求, 可以前往 [MasterYuan418/zxext](https://github.com/MasterYuan418/zxext) 查找或提出。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=anwenhu/zhixuewang-python&type=Date)](https://star-history.com/#anwenhu/zhixuewang-python&Date)
