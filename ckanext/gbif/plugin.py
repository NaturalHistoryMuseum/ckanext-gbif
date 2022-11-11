#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.gbif import routes
from ckanext.gbif.lib import helpers
from ckanext.gbif.logic.action import gbif_record_show


class GBIFPlugin(SingletonPlugin):
    '''GBIF plugin - Data Quality Indicators'''

    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IConfigurer)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.ITemplateHelpers)

    ## IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, 'theme/templates')
        toolkit.add_resource('theme/assets', 'ckanext-gbif')

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    def get_actions(self):
        return {'gbif_record_show': gbif_record_show}

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'dqi_get_severity': helpers.dqi_get_severity,
            'dqi_parse_errors': helpers.dqi_parse_errors,
            'gbif_get_classification': helpers.gbif_get_classification,
            'gbif_get_geography': helpers.gbif_get_geography,
            'gbif_render_datetime': helpers.gbif_render_datetime,
            'get_gbif_record_url': helpers.get_gbif_record_url,
            'build_gbif_nav_item': helpers.build_gbif_nav_item,
        }
