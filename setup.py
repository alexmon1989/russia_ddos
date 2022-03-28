from setuptools import setup, find_packages
from ripper.constants import VERSION

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='dripper',
    version=VERSION,
    url='https://github.com/alexmon1989/russia_ddos',
    python_requires=">=3.9",
    packages=find_packages(exclude=['tests']),
    install_requires=required,
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
    license='MIT'
)
