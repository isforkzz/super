from setuptools import setup, find_packages

setup(
    name="super-language",
    version="1.0.0",
    description="SuperStaticLanguage (.ssl) runner and CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "super=super.cli:main",
        ],
    },
    keywords=["language", "ssl", "superstaticlanguage", "runner", "interpreter"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
    ],
)
