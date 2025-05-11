from setuptools import setup, find_packages

setup(
    name="lzy",
    version="1.0.0",
    description="Translate natural language commands into Linux bash commands.",
    author="Ricardo Borges",
    author_email="ricardoborges@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "pydantic-ai",
        "python-dotenv",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "lzy=lzy.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)