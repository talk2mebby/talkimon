# setup.py

from setuptools import setup, find_packages

setup(
    name="talkimon",
    version="1.0.0",
    author="Talkimon Project",
    author_email="talkimon@gmail.com",  # optional
    description="Talkimon → The Universal AI → Real World Connector 🚀",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/talk2mebby/talkimon",
    packages=find_packages(where=".", exclude=["tests*", "build*", "*.egg-info"]),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.95",
        "uvicorn>=0.20",
        "requests>=2.25",
        "cryptography>=41.0",
        "pydantic>=1.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  # You're dual-licensing
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)

