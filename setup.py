#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

from setuptools import setup, find_packages

version = u'0.1'

setup(
	name=u'ckanext-gbif',
	version=version,
	description=u'GBIF',
	long_description=u'''GBIF Data Quality indicators''',
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords=u'',
	license=u'',
	packages=find_packages(exclude=[u'ez_setup', u'examples', u'tests']),
	namespace_packages=[u'ckanext', u'ckanext.gbif'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		u'requests',
		u'python-dateutil'
	],
	entry_points=\
	u'''
        [ckan.plugins]
            gbif = ckanext.gbif.plugin:GBIFPlugin
	''',
)
