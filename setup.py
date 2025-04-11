from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="configurational-llm",
    version="1.0.0",
    author="Trayten Yuming Zhang",
    author_email="author@example.com",
    description="A cross-platform application for processing scientific literature using large language models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/configurational-llm",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  # CC BY-NC-ND 4.0 is not in standard PyPI classifiers
        "Operating System :: OS Independent",
    ],
    license="CC BY-NC-ND 4.0",  # Attribution-NonCommercial-NoDerivatives 4.0 International
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "configurational_llm=main:main",
        ],
    },
    package_data={
        "": ["logos/*.png", "resources/translations/*.ts"],
    },
)
