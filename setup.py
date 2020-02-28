import sys
from shutil import rmtree
from setuptools import setup, Command, find_packages
import os
version = "1.0.1"
setup(
    name="zhixuewang",
    version=version,
    keywords=["智学网", "zhixue", "zhixuewang"],
    description="智学网的api",
    license="MIT",

    author="anwenhu",
    author_email="anemailpocket@163.com",

    packages=["zhixuewang", "zhixuewang.models", "zhixuewang.Student",
              "zhixuewang.Teacher", "zhixuewang.Student.models", "zhixuewang.Teacher.models"],
    include_package_data=True,
    platforms="any",
    install_requires=["requests"],
)
