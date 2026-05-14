"""Setup script for ag-falsifier package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ag-falsifier",
    version="0.1.0-alpha",
    author="Sergey Boyko",
    author_email="sergeikuch80@gmail.com",
    description="Falsification-first validation harness for AlphaGenome predictions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geoserg/ag-falsifier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ag-falsifier=ag_falsifier.cli:main",
        ],
    },
)
