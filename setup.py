import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="dict_to_dataclass",
    version="0.0.8",
    author="Daniel Jack",
    author_email="jackd68ed@googlemail.com",
    description=(
        "Utils for mapping dataclass fields to dictionary keys, making it possible to create an instance of a "
        "dataclass from a dictionary."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    url="https://github.com/jackd68ed/dict-to-dataclass",
)
