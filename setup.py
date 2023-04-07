from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ChatMastermind",
    version="0.1.0",
    author="Oleksandr Kozachuk",
    author_email="ddeus.lp@mailnull.com",
    description="A Python application to automate conversation with AI, store question+answer pairs, and compose chat history.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ok2/ChatMastermind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "openai",
        "PyYAML",
        "argcomplete",
        "pytest"
    ],
    python_requires=">=3.10",
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "cmm=chatmastermind.main:main",
        ],
    },
)
