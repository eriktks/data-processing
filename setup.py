#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('VERSION') as version_file:
    project_version = version_file.read()

setup(
    name='data-processing',
    version=project_version,
    description="Data processing scripts of the e-Mental Health project",
    long_description=readme + '\n\n',
    author="Erik Tjong Kim Sang",
    author_email='e.tjongkimsang@esciencecenter.nl',
    url='https://github.com/eriktks/data-processing',
    packages=[
        'data-processing',
    ],
    package_dir={'data-processing':
                 'data-processing'},
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='data-processing',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
)
