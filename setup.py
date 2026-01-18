#!/usr/bin/env python3
"""
Book Sort - 基于 AI 的智能图书分类系统
Setup configuration for pip installation
"""

from setuptools import setup, find_packages

setup(
    name="book-sort",
    version="1.0.0",
    description="基于 AI 的智能图书分类系统，使用 DeepSeek API 自动分类图书",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="whtoo",
    author_email="",
    url="https://github.com/whtoo/book_arrange",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.12.0",
        "SQLAlchemy>=2.0.0",
        "click>=8.0.0",
        "PyYAML>=6.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "book-sort=cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
