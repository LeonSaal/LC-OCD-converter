import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lcocd", 
    version="2024.12",
    author="Leon Saal",
    description="A package for converting and previewing LC-OCD-UV data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeonSaal/LC-OCD-converter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=["pandas", "matplotlib", "openpyxl", "lxml","xlwt",'odfpy'],
    python_requires=">=3.6",
)
