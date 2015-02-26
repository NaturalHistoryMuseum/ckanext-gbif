
import logging
import os
import dateutil.parser
from webhelpers.html import literal
from ckanext.gbif import GBIF_ERRORS


log = logging.getLogger(__name__)


def dqi_get_status_pill(dqi_status):
    """
    Convert a DQI status string into a class name
    @param dqi_status: Minor errors etc.,
    @return: minor-errors
    """

    cls = 'dqi-{0}'.format(dqi_status.lower().replace(' ', '-'))

    return literal(
        '''
        <span title="{0}" class="dqi-pill {1}">{0}</span>
        '''.format(dqi_status, cls))


def gbif_get_classification(occurrence):
    """
    Loop through all the classification parts, building an array of parts
    @param occurrence:
    @return:
    """

    classification = []

    url = 'http://www.gbif.org/species'

    for classification_part in [u'kingdom', u'phylum', u'class', u'order', u'family', u'genus']:
        key = '%sKey' % classification_part

        key_value = occurrence.get(key, None)
        name = occurrence.get(classification_part, None)

        if key_value:
            classification.append('<a href="{href}" target="_blank" rel="nofollow">{name}</a>'.format(
                href=os.path.join(url, str(key_value)),
                name=name
            ))
        elif name:
            classification.append(name)

    return literal(' <i class="icon-double-angle-right"></i> '.join(classification))


def gbif_get_geography(occurrence):

    geography = []
    for geographic_part in [u'continent', u'country', u'stateProvince']:

        value = occurrence.get(geographic_part, None)

        if value:
            geography.append(value.replace('_', ' '))

    return literal(' <i class="icon-double-angle-right" /> '.join(geography))

def gbif_get_errors():
    return GBIF_ERRORS

def gbif_format_date(date_str):
    return dateutil.parser.parse(date_str).strftime("%B %d, %Y. %X")

