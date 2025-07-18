"""
Setup script for WCS Analysis Platform
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wcs-analysis-platform",
    version="1.0.0",
    author="WCS Analysis Team",
    author_email="support@wcs-analysis.com",
    description="A professional Streamlit application for Worst Case Scenario analysis of GPS data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wcs-analysis-platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Sports",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wcs-app=src.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="gps, sports, analysis, worst case scenario, performance, streamlit",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wcs-analysis-platform/issues",
        "Source": "https://github.com/yourusername/wcs-analysis-platform",
        "Documentation": "https://github.com/yourusername/wcs-analysis-platform/docs",
    },
) 