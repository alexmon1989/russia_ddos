from setuptools import setup, find_packages
from ripper.constants import VERSION

with open('requirements.txt', 'r', encoding='utf-8') as f:
    required = f.read().splitlines()

with open('README.md', 'r', encoding='utf-8') as md:
    readme = md.read()

setup(
    name='dripper',
    version=VERSION,
    long_description=readme,
    long_description_content_type='text/markdown',
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
