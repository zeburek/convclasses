#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "dataclasses == 0.7; python_version=='3.6'",
]

dev_reqs = [
    "bumpversion",
    "wheel",
    "watchdog",
    "flake8",
    "tox",
    "coverage",
    "Sphinx",
    "pytest",
    "hypothesis",
    "arrow",
]

setup(
    name="convclasses",
    version="1.0.0",
    description="Complex custom class converters for dataclasses",
    long_description=readme + "\n\n" + history,
    author="Parviz Khavari",
    author_email="me@parviz.pw",
    url="https://github.com/zeburek/convclasses",
    packages=find_packages(where="src", exclude=["tests*"]),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    extras_require={"dev": dev_reqs},
    license="MIT license",
    zip_safe=False,
    keywords="convclasses",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
