#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '6/2/16 2:55 PM'
__description__ = '''
安装:
1. sudo -H pip install izen
2. sudo -H python setup.py install --record izen_install.log

删除方式:
1. sudo -H pip uninstall izen
2. cat izen_install.log | xargs sudo rm -rf

'''

from setuptools import setup, find_packages

VERSION = '0.2.1'

setup(
    name='izen',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/izen',
    description='encapsulation of some useful features',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[
        'bs4',
        'click',
        'clint',
        'hot_redis',
        'logzero',
        'numpy',
        'paho-mqtt',
        'profig',
        'psutil',
        'pycryptodome',
        'requests',
        'selenium',
        'tqdm',
        'wcwidth',
    ],
    keywords=['izen', 'tool']
)
