from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-gbif',
	version=version,
	description="",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.gbif'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
            gbif = ckanext.gbif.plugin:GBIFPlugin
	""",
)
