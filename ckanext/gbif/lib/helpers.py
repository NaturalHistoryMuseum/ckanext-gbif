#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import logging

import dateutil.parser
import os
from ckanext.gbif.lib.errors import DQI_MAJOR_ERRORS, GBIF_ERRORS
from webhelpers.html import literal

log = logging.getLogger(__name__)


def dqi_parse_errors(dqi):
    '''Convert a DQI status string into a class name

    :param dqi: Minor errors etc.,
    :returns: minor-errors

    '''

    errors = []
    # BS: Hacky bug fix - DQIs are passed in as a list on record view, but not on GBIF
    #  page!
    dqi = dqi[0] if isinstance(dqi, list) else dqi
    try:
        error_codes = dqi.split(u';')
    except (AttributeError, TypeError):
        pass
    else:
        for error_code in error_codes:
            errors.append(GBIF_ERRORS[error_code])
    return errors


def dqi_get_severity(errors, gbif_id):
    '''Get class name for severity of errors

    :param errors: param gbif_id:
    :param gbif_id: 

    '''

    if not gbif_id:
        return u'unknown'

    if not errors:
        return u'No errors'

    for error in errors:
        if error[u'severity'] == DQI_MAJOR_ERRORS:
            # If we have one major error, the whole thing is major error
            return u'Major errors'

    return u'Minor errors'


def gbif_get_classification(gbif_record):
    '''Loop through all the classification parts, building an array of parts

    :param gbif_record: return:

    '''
    classification = []

    url = u'http://www.gbif.org/species'
    for classification_part in [u'kingdom', u'phylum', u'class', u'taxonorder',
                                u'family', u'genus']:
        key = u'%skey' % classification_part
        key_value = gbif_record.get(key, None)
        name = gbif_record.get(classification_part, None)
        if key_value:
            classification.append(
                u'<a href="{href}" target="_blank" rel="nofollow">{name}</a>'.format(
                    href=os.path.join(url, str(key_value)),
                    name=name
                    ))
        elif name:
            classification.append(name)

    return literal(u' <i class="icon-angle-right"></i> '.join(classification))


def gbif_get_geography(occurrence):
    '''

    :param occurrence: 

    '''
    geography = []
    for geographic_part in [u'continent', u'country', u'stateprovince']:

        value = occurrence.get(geographic_part, None)

        if value:
            geography.append(value.replace(u'_', u' '))

    return literal(u' <i class="icon-angle-right"></i> '.join(geography))


def gbif_render_datetime(date_str):
    '''Render a GBIF formatted datetime

    :param date_str: return:

    '''
    return dateutil.parser.parse(date_str).strftime(u'%B %d, %Y')
