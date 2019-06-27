import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='monobankua',
    version='0.0.4',
    author='Sergey Shlyapugin',
    author_email='shlyapugin@gmail.com',
    description='Monobank.ua API client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/inbalboa/python-monobankua',
    packages=setuptools.find_packages(),
    install_requires=['requests>=2.21,<3.0'],
    python_requires='>=3.7,<4.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
