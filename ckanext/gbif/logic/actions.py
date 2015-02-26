import json
import pylons
import ckan.logic as logic
from ckan.plugins import toolkit
from ckanext.gbif import GBIF_ERRORS, DQI_UNKNOWN, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS, DQI_NO_ERRORS
from ckanext.datastore.db import _get_engine

_get_or_bust = logic.get_or_bust

def update_record_dqi(context, data_dict, **kw):
    """ Update the DQI of a record based on a list of GBIF errors

    @param context: CKAN context
    @param data_dict: Action parameters:
        - resource_id: The resource id to update (required)
        - records: List of dictionary of values to update
                Required: occurrence_id, errors, gbif_id

    """

    # TODO: Access check
    # p.toolkit.check_access('update_record_dqi', context, data_dict)

    # We must have resource ID
    resource_id = _get_or_bust(data_dict, "resource_id")

    # Set up DB connection to datastore
    connection = _get_engine({'connection_url': pylons.config['ckan.datastore.write_url']}).connect()

    # Create a dictionary of two sets, containing major and minor errors
    error_types = {}
    for error_type in [DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS]:
        error_types[error_type] = set([error for error, info in GBIF_ERRORS.iteritems() if info['severity'] == error_type])

    # Base SQL statement - Update multiple entries at a time
    sql = """
        UPDATE "{resource_id}"
        AS r
        SET "dqi" = v."dqi", "_gbif_id" = v."_gbif_id"
        FROM (VALUES {update_values}) as v("occurrenceID", dqi, _gbif_id)
        WHERE r."occurrenceID" = v."occurrenceID"::uuid;
    """

    # List of values to update
    update_values = list()

    # Loop through each of the records, building update_values list
    for record_dict in data_dict['records']:

        # Must contain occurrence ID
        occurrence_id = _get_or_bust(record_dict, "occurrence_id")
        errors = record_dict.get('errors')
        gbif_id = record_dict.get('gbif_id')

        # Map the status
        dqi_status = DQI_UNKNOWN
        if len(errors) == 0:
            dqi_status = DQI_NO_ERRORS
        if error_types[DQI_MAJOR_ERRORS].intersection(errors):
            dqi_status = DQI_MAJOR_ERRORS
        elif error_types[DQI_MINOR_ERRORS].intersection(errors):
            dqi_status = DQI_MINOR_ERRORS

        update_values.append("('%s', '%s', %s)" % (occurrence_id, dqi_status, int(gbif_id)))

    result = connection.execute(sql.format(
        resource_id=resource_id,
        update_values=','.join(update_values))
    )

    return result.rowcount