from setuptools import setup, find_packages
from ripper.constants import VERSION

setup(
    name='dripper',
    version=VERSION,
    packages=['ripper'],
    install_requires=['rich==12.0.0', 'pysocks==1.7.1'],
    package_data={
        'ripper': [
            'headers.txt',
            'useragents.txt',
        ],
    },
    entry_points={
        'console_scripts': [
            'dripper=ripper.services:cli',
        ],
    },
)
