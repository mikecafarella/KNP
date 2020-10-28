import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kgpl_client", # Replace with your own username
    version="1.0.0",
    author="KNP team",
    author_email="michjc@umich.edu",
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
    python_requires='>=3.6',
)