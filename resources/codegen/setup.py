from setuptools import setup, find_packages


setup(
    name="openassetio-codegen",
    version="1.0.0-alpha.1",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["jinja2==3.1.2", "pyyaml==5.4.1", "jsonschema==4.7.2"],
    entry_points={
        "console_scripts": ["openassetio-codegen=openassetio_codegen.__main__:main"],
    },
)
