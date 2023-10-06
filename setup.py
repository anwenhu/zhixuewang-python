from setuptools import setup, find_packages

version = "1.2.3"
setup(
    name="zhixuewang",
    version=version,
    keywords=["智学网", "zhixue", "zhixuewang"],
    description="智学网的api",
    license="MIT",

    author="anwenhu,MasterYuan418,immoses648",
    author_email="anemailpocket@163.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests"]
)
