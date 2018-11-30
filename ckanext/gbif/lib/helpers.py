import logging
import os
import dateutil.parser
from pylons import config
import ckan.plugins.toolkit as toolkit
from webhelpers.html import literal
from ckanext.gbif.lib.errors import GBIF_ERRORS, DQI_MAJOR_ERRORS

log = logging.getLogger(__name__)


def dqi_parse_errors(errors):
    """
    Convert each DQI status string into a more detailed dict.

    :param errors: a list of error names
    :return: a list of dicts of information about each error
    """
    return [GBIF_ERRORS[error_code] for error_code in errors] if errors else []


def dqi_get_severity(errors, gbif_id):
    """
    Get status for severity of errors.

    :param errors: a list of errors
    :param gbif_id: the GBIF occurrence id for this record
    :return: the status to show
    """
    if not gbif_id:
        return 'unknown'

    if not errors:
        return 'No errors'

    for error in errors:
        if error['severity'] == DQI_MAJOR_ERRORS:
            # if we have one major error, the whole thing is major error
            return 'Major errors'

    return 'Minor errors'


def gbif_get_classification(gbif_record):
    """
    Loop through all the classification parts, building an array of parts
    @param gbif_record:
    @return:
    """
    classification = []

    url = 'http://www.gbif.org/species'
    for classification_part in ['kingdom', 'phylum', 'class', 'taxonorder', 'family', 'genus']:
        key = '%sKey' % classification_part
        key_value = gbif_record.get(key, None)
        name = gbif_record.get(classification_part, None)
        if key_value:
            classification.append('<a href="{href}" target="_blank" rel="nofollow">{name}</a>'.format(
                href=os.path.join(url, str(key_value)),
                name=name
            ))
        elif name:
            classification.append(name)

    return literal(' <i class="icon-angle-right"></i> '.join(classification))


def gbif_get_geography(occurrence):
    geography = []
    for geographic_part in ['continent', 'country', 'stateprovince']:

        value = occurrence.get(geographic_part, None)

        if value:
            geography.append(value.replace('_', ' '))

    return literal(' <i class="icon-angle-right"></i> '.join(geography))


def gbif_render_datetime(date_str):
    """
    Render a GBIF formatted datetime
    :param date_str:
    :return:
    """
    return dateutil.parser.parse(date_str).strftime("%B %d, %Y")


def get_gbif_record_url(pkg, res, rec):
    '''
    Given details about a combination of package, resource and record, return the GBIF view URL created from them.
    :param pkg: the package dict
    :param res: the resource dict
    :param rec: the record dict
    :return: the link to the GBIF view for this record/resource/package combo
    '''
    # find the gbif route defined in the plugin definition
    gbif_route = config['routes.named_routes']['gbif']
    # return the url for package/resource/record combo requested
    return toolkit.url_for(controller=gbif_route['controller'], action=gbif_route['action'], package_name=pkg['name'],
                           resource_id=res['id'], record_id=rec['_id'])
