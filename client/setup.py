import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="knps",  # Replace with your own username
    version="1.0.0",
    author="KNP team",
    author_email="KNPS-Group@umich.edu",
    description="KNP client pacakge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikecafarella/KNP",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
            'requests',
            'pandas',
            'numpy',
            'SPARQLWrapper',
            'bs4',
            'pyyaml',
            'flask',
            'bsddb3',
            'dill'
    ],
    python_requires='>=3.6',
)


