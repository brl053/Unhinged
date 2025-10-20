#!/usr/bin/env python3
"""Setup script for Unhinged Proto Clients (Python)"""

from setuptools import setup, find_packages

setup(
    name="unhinged-proto-clients",
    version="1.0.0",
    description="Generated Python protobuf clients for Unhinged platform",
    author="Unhinged Team",
    author_email="team@unhinged.dev",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "protobuf>=4.21.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="protobuf grpc unhinged",
)
