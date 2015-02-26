import os
import ckan.plugins as p
import pylons
from ckanext.datastore.db import _get_engine
from ckanext.gbif.logic.actions import update_record_dqi
from ckanext.gbif.lib.helpers import (
    dqi_get_status_pill,
    gbif_get_geography,
    gbif_get_classification,
    gbif_get_errors,
    gbif_format_date
)


class GBIFPlugin(p.SingletonPlugin):
    """
    GBIF plugin - Data Quality Indicators
    """
    p.implements(p.IActions, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IRoutes, inherit=True)

    ## IConfigurable
    def configure(self, config):
        """
        Called at the end of CKAN setup.
        Create DOI table
        """
        self._create_gbif_id_column(pylons.config['ckanext.gbif.resource_id'])

    @staticmethod
    def _create_gbif_id_column(resource_id):
        """
        Create a column to store the GBIF ID, if it doesn't already exist
        @param resource_id:
        @return:
        """

        resource_id = pylons.config['ckanext.gbif.resource_id']
        column_name = '_gbif_id'

        try:
            connection = _get_engine({'connection_url': pylons.config['ckan.datastore.write_url']}).connect()
            # Check if the column exists
            exists = connection.execute(u'''
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='{0}' AND column_name='{1}';
            '''.format(resource_id, column_name)).scalar()

            # If the GBIF column does not already exist, add it
            if not exists:
                # Add the GBIF ID column
                connection.execute(u'ALTER TABLE "{0}" ADD COLUMN {1} int;'.format(resource_id, column_name))
                # Add GBIF ID unique constraint - fails
                # connection.execute(u'ALTER TABLE "{0}" ADD UNIQUE ({1});'.format(resource_id, column_name))

        finally:
            connection.close()

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
            'update_record_dqi':  update_record_dqi
        }

    # ITemplateHelpers
    def get_helpers(self):

        return {
            'dqi_get_status_pill': dqi_get_status_pill,
            'gbif_get_classification': gbif_get_classification,
            'gbif_get_geography': gbif_get_geography,
            'gbif_get_errors': gbif_get_errors,
            'gbif_format_date': gbif_format_date
        }