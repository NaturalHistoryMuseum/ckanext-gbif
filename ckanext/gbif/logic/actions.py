import json
import ckan.logic as logic
from ckan.plugins import toolkit
from ckanext.gbif.plugin import DQI_UNKNOWN, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS, DQI_NO_ERRORS
from ckanext.datastore.db import _get_unique_key

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
        - filters: The filters to select the records to update (as a
                   dictionary). (required)
        - errors: The list of GBIF errors (required)
        - force: True to edit a read only resource (optional, defaults to False)
    """
    # Validate the request parameters
    resource_id = _get_or_bust(data_dict, "resource_id")

    if isinstance(data_dict['filters'], basestring):
        try:
            filters = json.loads(data_dict['filters'])
        except ValueError:
            raise toolkit.Invalid()
    else:
        filters = data_dict['filters']

    if isinstance(data_dict['errors'], basestring):
        try:
            errors = json.loads(data_dict['errors'])
        except ValueError:
            raise toolkit.Invalid()
    else:
        errors = data_dict['errors']

    if 'force' not in data_dict:
        force = False
    elif isinstance(data_dict['force'], basestring):
        force = data_dict['force'].lower() == 'true'
    else:
        force = data_dict['force']

    # Map the status
    status = DQI_UNKNOWN
    if len(errors) == 0:
        status = DQI_NO_ERRORS
    if MAJOR_ERRORS.intersection(errors):
        status = DQI_MAJOR_ERRORS
    elif MINOR_ERRORS.intersection(errors):
        status = DQI_MINOR_ERRORS

    # Get the _id of the record(s)
    result = toolkit.get_action('datastore_search')({}, {
        'resource_id': resource_id,
        'filters': filters
    })

    # Update the record(s)
    rows = []
    for result_row in result['records']:
        r = dict([(f, result_row[f]) for f in result_row if not f.startswith('_')])
        r['dqi'] = status
        rows.append(r)

    toolkit.get_action('datastore_upsert')({}, {
        'resource_id': resource_id,
        'method': 'update',
        'records': rows,
        'force': force
    })