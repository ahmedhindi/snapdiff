from setuptools import setup, find_packages

setup(
    name="snapdiff",
    version="0.1.0",
    description="A package for comparing snapshots of data and tracking differences when function change",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ahmed Hendy",
    author_email="ahmedelsyd5@gmail.com",
    url="https://github.com/ahmedhendy/snapdiff",
    packages=find_packages(),
    install_requires=[],  # Include dependencies or use requirements.txt as you have
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
