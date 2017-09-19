import pylons
import ckan.logic as logic
from ckanext.datastore.db import _get_engine
from ckanext.datastore.db import _execute_single_statement

_get_or_bust = logic.get_or_bust
NotFound = logic.NotFound


def gbif_record_show(context, data_dict):
    """ Update the DQI of a record based on a list of GBIF errors
    @param context: CKAN context
    @param data_dict: Action parameters:
        - occurrence_id
    """
    occurrence_id = _get_or_bust(data_dict, 'occurrence_id')
    # Set up DB connection to datastore
    context['connection'] = _get_engine({'connection_url': pylons.config['ckan.datastore.read_url']}).connect()
    sql = 'SELECT * FROM gbif WHERE occurrenceid=%s LIMIT 1'
    result = _execute_single_statement(context, sql, occurrence_id)
    record = result.fetchone()
    if record:
        return dict(record)
    else:
        raise NotFound