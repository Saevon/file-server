#!/usr/bin/env python
import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

install_requires = []
with open("requirements.txt", "r") as requirements_file:
    install_requirements = requirements_file.read().splitlines()

install_requirements = [
    require for require in install_requirements
    # Don't include empty requirements
    if require.strip() != '' and
    # Allow comments too (remove them)
    not require.strip().startswith('#')
]


setuptools.setup(
    name='Simple File Server',
    version='1.0',

    description='Allows transfering files using a http server',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Saevon Kyomae',
    author_email='saevon.kyomae@gmail.com',
    url='',

    packages=setuptools.find_packages(
        exclude=['contrib', 'docs', 'tests'],
    ),
    entry_points={
        'console_scripts': [
            'file_server = file_server:main',
        ],
    },
    install_requires=install_requires,
)
