from setuptools import setup, find_packages

version = "1.1.6"
setup(
    name="zhixuewang",
    version=version,
    keywords=["智学网", "zhixue", "zhixuewang"],
    description="智学网的api",
    license="MIT",

    author="anwenhu",
    author_email="anemailpocket@163.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests", "httpx", "numpy<=1.21", "rsa"],
)
