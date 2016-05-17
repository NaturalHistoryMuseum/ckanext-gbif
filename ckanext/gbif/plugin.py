import os
import pylons
import ckan.plugins as p
from ckanext.datastore.interfaces import IDatastore
from ckanext.gbif.logic.action import gbif_record_show
from ckanext.gbif.lib.helpers import (
    dqi_parse_errors,
    dqi_get_severity,
    gbif_get_geography,
    gbif_get_classification,
    gbif_render_datetime
)


class GBIFPlugin(p.SingletonPlugin):
    """
    GBIF plugin - Data Quality Indicators
    """
    p.implements(p.IActions, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(IDatastore, inherit=True)

    ## IConfigurer
    def update_config(self, config):

        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(root_dir, 'ckanext', 'gbif', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-gbif')

    ## IRoutes
    def before_map(self, map):

        # Add GBIF record view
        map.connect('gbif', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/gbif',
            controller='ckanext.gbif.controllers.gbif:GBIFController',
            action='view'
        )

        return map

    def get_actions(self):
        return {
            'gbif_record_show':  gbif_record_show
        }

    # ITemplateHelpers
    def get_helpers(self):

        return {
            'dqi_get_severity': dqi_get_severity,
            'dqi_parse_errors': dqi_parse_errors,
            'gbif_get_classification': gbif_get_classification,
            'gbif_get_geography': gbif_get_geography,
            'gbif_render_datetime': gbif_render_datetime
        }

    ## IDataStore
    def datastore_search(self, context, data_dict, all_field_ids, query_dict):

        resource_id = pylons.config['ckanext.nhm.specimen_resource_id']

        # print all_field_ids
        if resource_id == data_dict['resource_id']:
            # Add the issue field to the query
            query_dict['select'].insert(1, '"gbifIssue"')
            # And add the GBIF ID - wen can use this in the template to check
            # if we have a GBIF record
            query_dict['select'].append('"gbifID"')
            query_dict['ts_query'] = 'LEFT JOIN gbif.occurrence ON "gbifOccurrenceID" = "occurrenceID"'

        return query_dict