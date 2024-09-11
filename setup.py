from setuptools import setup, find_packages

setup(
    name="opengradient",
    version="0.1.0",
    packages=['opengradient'],
    package_dir={'opengradient': 'src'},
    install_requires=[
        "requests",
        "onnx",
        # other dependencies
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
)