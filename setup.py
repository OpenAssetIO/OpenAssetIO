from setuptools import setup, find_packages

setup(
    name='openassetio',
    version="1.0.0-alpha.2",
    package_dir={'': 'python'},
    packages=find_packages(where='python'),
    python_requires='>=3.7',
)
