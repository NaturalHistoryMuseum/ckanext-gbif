import json
import pylons
import ckan.logic as logic
from ckan.plugins import toolkit
from ckanext.gbif.plugin import DQI_UNKNOWN, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS, DQI_NO_ERRORS
from ckanext.datastore.db import _get_engine

_get_or_bust = logic.get_or_bust

MAJOR_ERRORS = set([
    'TYPE_STATUS_INVALID',
    'TAXON_MATCH_NONE',
    'BASIS_OF_RECORD_INVALID',
])

MINOR_ERRORS = set([
    'ZERO_COORDINATE',
    'COORDINATE_OUT_OF_RANGE',
    'COORDINATE_INVALID',
    'COORDINATE_ROUNDED',
    'GEODETIC_DATUM_INVALID',
    'GEODETIC_DATUM_ASSUMED_WGS84',
    'COORDINATE_REPROJECTED',
    'COORDINATE_REPROJECTION_FAILED',
    'COORDINATE_REPROJECTION_SUSPICIOUS',
    'COUNTRY_COORDINATE_MISMATCH',
    'COUNTRY_MISMATCH',
    'COUNTRY_INVALID',
    'COUNTRY_DERIVED_FROM_COORDINATES',
    'CONTINENT_COUNTRY_MISMATCH',
    'CONTINENT_INVALID',
    'CONTINENT_DERIVED_FROM_COORDINATES',
    'PRESUMED_SWAPPED_COORDINATE',
    'PRESUMED_NEGATED_LONGITUDE',
    'PRESUMED_NEGATED_LATITUDE',
    'RECORDED_DATE_MISMATCH',
    'RECORDED_DATE_INVALID',
    'RECORDED_DATE_UNLIKELY',
    'TAXON_MATCH_FUZZY',
    'TAXON_MATCH_HIGHERRANK',
    'DEPTH_NOT_METRIC',
    'DEPTH_UNLIKELY',
    'DEPTH_MIN_MAX_SWAPPED',
    'DEPTH_NON_NUMERIC',
    'ELEVATION_UNLIKELY',
    'ELEVATION_MIN_MAX_SWAPPED',
    'ELEVATION_NOT_METRIC',
    'ELEVATION_NON_NUMERIC',
    'MODIFIED_DATE_INVALID',
    'MODIFIED_DATE_UNLIKELY',
    'IDENTIFIED_DATE_UNLIKELY',
    'IDENTIFIED_DATE_INVALID',
    'MULTIMEDIA_DATE_INVALID',
    'MULTIMEDIA_URI_INVALID',
    'REFERENCES_URI_INVALID'
])


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
        if MAJOR_ERRORS.intersection(errors):
            dqi_status = DQI_MAJOR_ERRORS
        elif MINOR_ERRORS.intersection(errors):
            dqi_status = DQI_MINOR_ERRORS

        update_values.append("('%s', '%s', %s)" % (occurrence_id, dqi_status, int(gbif_id)))

    result = connection.execute(sql.format(
        resource_id=pylons.config['ckanext.gbif.resource_id'],
        update_values=','.join(update_values))
    )

    return result.rowcount