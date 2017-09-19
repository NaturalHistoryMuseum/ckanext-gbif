import logging
import os
import dateutil.parser
from webhelpers.html import literal
from ckanext.gbif.lib.errors import GBIF_ERRORS, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS

log = logging.getLogger(__name__)


def dqi_parse_errors(dqi):
    """
    Convert a DQI status string into a class name
    @param dqi_status: Minor errors etc.,
    @return: minor-errors
    """

    errors = []
    try:
        error_codes = dqi.split(';')
    except AttributeError:
        pass
    else:
        for error_code in error_codes:
            errors.append(GBIF_ERRORS[error_code])
    return errors


def dqi_get_severity(errors, gbif_id):
    """
    Get class name for severity of errors
    :param errors:
    :param gbif_id:
    :return:
    """

    if not gbif_id:
        return 'unknown'

    if not errors:
        return 'No errors'

    for error in errors:
        if error['severity'] == DQI_MAJOR_ERRORS:
            # If we have one major error, the whole thing is major error
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
        key = '%skey' % classification_part
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
