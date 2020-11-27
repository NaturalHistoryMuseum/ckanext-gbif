#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import os

from ckanext.gbif.lib.helpers import (
    dqi_parse_errors,
    dqi_get_severity,
    gbif_get_geography,
    gbif_get_classification,
    gbif_render_datetime,
    get_gbif_record_url,
    build_gbif_nav_item)
from ckanext.gbif.logic.action import gbif_record_show
from ckanext.gbif import routes

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.datastore.interfaces import IDatastore


class GBIFPlugin(SingletonPlugin):
    '''GBIF plugin - Data Quality Indicators'''
    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IConfigurer)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.ITemplateHelpers)
    implements(IDatastore, inherit=True)

    ## IConfigurer
    def update_config(self, config):
        '''

        :param config:

        '''
        toolkit.add_template_directory(config, u'theme/templates')
        toolkit.add_resource(u'theme/assets', u'ckanext-gbif')

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    def get_actions(self):
        ''' '''
        return {
            u'gbif_record_show': gbif_record_show
            }

    # ITemplateHelpers
    def get_helpers(self):
        ''' '''
        return {
            u'dqi_get_severity': dqi_get_severity,
            u'dqi_parse_errors': dqi_parse_errors,
            u'gbif_get_classification': gbif_get_classification,
            u'gbif_get_geography': gbif_get_geography,
            u'gbif_render_datetime': gbif_render_datetime,
            u'get_gbif_record_url': get_gbif_record_url,
            u'build_gbif_nav_item': build_gbif_nav_item,
        }
