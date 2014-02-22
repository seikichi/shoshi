#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.0.1'

setup(name='shoshi',
      version=version,
      description="",
      long_description="""""",
      classifiers=[
      ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='amazon wikipedia NDL book metadata',
      author='seikichi',
      author_email='seikichi@kmc.gr.jp',
      url='https://github.com/seikichi/shoshi',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'mwparserfromhell',
          'bottlenose',
          'requests',
          'lxml',
      ])
