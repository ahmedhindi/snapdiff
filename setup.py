from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    required = f.read().splitlines()

# Setup function
setup(
    name="snapdiff",  # The name of your package
    version="0.1.0",  # Initial version
    author="Ahmed Hendy",  # Replace with your name
    author_email="ahmedelsyd5@gmail.com",  # Replace with your email
    description="A package for comparing snapshots of data and tracking differences when function change",
    long_description=open("README.md").read(),  # This will read from a README.md file
    long_description_content_type="text/markdown",  # If your README is in Markdown
    url="https://github.com/ahmedhindi/snapdiff",  # Your project's GitHub URL
    packages=find_packages(),  # Automatically find and include all packages in your project
    install_requires=required,  # Install dependencies from requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify the minimum Python version
)
