from setuptools import setup, find_packages

setup(
    name="opengradient",
    version="0.1.0",
    packages=find_packages(exclude=['@test_nb*', '@tests*', 'tests', '*.tests', '*.tests.*']),
    package_dir={'opengradient': 'src'},
    install_requires=[
        "requests",
        "onnx",
        "pytest",
        "web3",
        "skl2onnx",
        "firebase-rest-api",
        "onnxmltools",
        "pyarrow",
        "fastparquet",
        "onnxruntime"
    ],
    author="OpenGradient",
    author_email="oliver@opengradient.ai",
    description="A Python SDK for OpenGradient inference services",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/OpenGradient",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_data={
        'opengradient': ['*.py'],
    },
    exclude_package_data={
        '': ['*.ipynb', '*.pyc', '*.pyo', '.gitignore', 'requirements.txt', 'conftest.py'],
        'opengradient': ['opengradient.egg-info/*'],
    },
)