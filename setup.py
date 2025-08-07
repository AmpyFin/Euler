#!/usr/bin/env python3
"""
Setup script for Euler Market Analysis System.
"""
from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Dependencies are now managed in pyproject.toml
# This setup.py is kept for compatibility but relies on pyproject.toml for dependencies

setup(
    name="euler-market-analysis",
    version="1.0.0",
    author="Euler Team",
    author_email="team@euler.com",
    description="A comprehensive market analysis system for real-time risk assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/euler/market-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    # Dependencies are managed in pyproject.toml
    install_requires=[],
    extras_require={
        "test": [],
        "dev": [],
    },
    entry_points={
        "console_scripts": [
            "euler=clients.system_client:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    zip_safe=False,
    keywords="market analysis, risk assessment, financial indicators, vix, volatility",
    project_urls={
        "Bug Reports": "https://github.com/euler/market-analysis/issues",
        "Source": "https://github.com/euler/market-analysis",
        "Documentation": "https://euler-market-analysis.readthedocs.io/",
    },
)
