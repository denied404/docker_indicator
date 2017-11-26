from setuptools import setup
import os


__author__ = "Anton Lvov"


datadir = os.path.join('img')
datafiles = [(d, [os.path.join(d, f) for f in files])
             for d, folders, files in os.walk(datadir)]


setup(
    name="docker-indicator",
    version="0.0.1",
    packages=["indicator"],
    package_dir={"indicator": "src/"},
    install_requires=["docker", "vext", "vext.gi"],
    include_package_data=True,
    entry_points={
        "console_scripts": ["docker-indicator=indicator:main"]
    },
    data_files=datafiles
)
