#!/usr/bin/env

from setuptools import find_packages, setup

setup(
    name='dfs_sdk',
    version='1.0.1',
    description='Datera Fabric Python SDK',
    long_description='Install Instructions: sudo python setup.py install',
    author='Datera Automation Team',
    author_email='support@datera.io',
    packages=['dfs_sdk'],
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=[],
    scripts=['utils/dhutil']
)
