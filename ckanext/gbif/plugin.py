DQI_NA = 'N/A'
DQI_UNKNOWN = 'Unknown'
DQI_MAJOR_ERRORS = 'Major errors'
DQI_MINOR_ERRORS = 'Minor errors'
DQI_NO_ERRORS = 'No errors'

import ckan.plugins as p
from ckanext.gbif.logic.actions import update_record_dqi


class GBIFPlugin(p.SingletonPlugin):
    """
    GBIF plugin - Data Quality Indicators
    """
    p.implements(p.IActions, inherit=True)
    def get_actions(self):
        return {
            'update_record_dqi':  update_record_dqi
        }