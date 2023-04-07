import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BaseBot",
    version="0.1.0",
    author="Sergiy Bokhnyak",
    author_email="sergeybok@gmail.com",
    description="BaseBot for creating bot backends easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sergeybok/BaseBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
