from setuptools import setup, find_packages

setup(
    name="xuan",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'xuan=xuan.cli:main',
        ],
    },
    author="rufatkiu",
    author_email="official@wl.ax",
    description="玄语言 - 一个中文编程语言",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Metastem/xuan",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
