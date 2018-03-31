#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '6/2/16 2:55 PM'
__description__ = '''
安装:
sudo -H python setup.py install
sudo -H python setup.py install --record izen_install.log

删除方式:
sudo -H pip uninstall izen
cat izen_install.log | xargs sudo rm -rf

'''

from setuptools import setup, find_packages
import izen

setup(
    name='izen',
    version=izen.VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url=' ',
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License"
    ],
    install_requires=[
        'click',
        'clint',
        'logzero',
        'profig',
        'psutil',
        'pycrypto',
        'hot-redis',
        'paho-mqtt',
        'wcwidth',
    ],
    description='encapsulation of some useful feature',
)
