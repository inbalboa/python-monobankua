from pathlib import Path

import setuptools


def long_description():
    return Path('README.md').read_text(encoding='utf-8')


def find_requires():
    with Path('requirements.txt').open(encoding='utf-8') as reqs:
        return reqs.readlines()


def find_version():
    with Path('VERSION').open(encoding='utf-8') as ver:
        return ver.readline().strip()


setuptools.setup(
    name='monobankua',
    version=find_version(),
    author='Serhiy Shliapuhin',
    author_email='shlyapugin@gmail.com',
    description='Monobank.ua API client',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/inbalboa/python-monobankua',
    packages=setuptools.find_packages(),
    install_requires=find_requires(),
    python_requires='>=3.10,<4.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
    ],
    license_expression='GPL-3.0-only',
    license_files=['LICENSE'],
)
