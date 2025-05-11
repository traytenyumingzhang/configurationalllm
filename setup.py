from setuptools import setup, find_packages
import sys
import os

# --- Helper to add venv site-packages to sys.path ---
# This might help py2app find namespace packages like 'google'
# Get the directory of the setup.py script
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the path to the site-packages directory in the .venv
venv_site_packages = os.path.join(script_dir, ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")

# Add to sys.path if it exists and is not already there
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
# --- End Helper ---


# Basic app information
APP_NAME = "ConfigurationalLLM"
APP_SCRIPT = "main.py"
VERSION = "1.0.1"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

# py2app specific options
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'PySide6',
        'requests',
        # 'google', # Let includes handle google more explicitly
        'anthropic',
        'openai',
        'pandas',
        'PyPDF2',
        'PIL'
    ],
    'includes': [
        'google',
        'google.auth',
        'google.generativeai',
        'google.ai',
        'google.api_core',
        'google.protobuf', # Added protobuf
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
    ],
    'resources': [
        'logos',
        'resources'
    ],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'CFBundleIdentifier': f"com.configurational.tech.{APP_NAME.lower()}",
        'NSHumanReadableCopyright': '© configurational.tech contributors'
    },
    'excludes': ['PyInstaller', 'setuptools._vendor.packaging', 'setuptools._vendor.wheel']
}

setup(
    name="configurational-llm",
    version=VERSION,
    author="Trayten Yuming Zhang",
    author_email="author@example.com",
    description="A cross-platform application for processing scientific literature using large language models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/configurational-llm",
    packages=find_packages(include=['gui', 'gui.*', 'core', 'core.*', 'utils', 'utils.*', 'google', 'google.*']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: MacOS :: MacOS X",
    ],
    license="CC BY-NC-ND 4.0",
    python_requires=">=3.8",
    install_requires=requirements,

    app=[APP_SCRIPT],
    data_files=[],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
