#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import logging

import dateutil.parser
from ckan.lib.helpers import literal
from ckan.plugins import toolkit

from ckanext.gbif.lib.errors import DQI_MAJOR_ERRORS, GBIF_ERRORS

log = logging.getLogger(__name__)


def dqi_parse_errors(errors):
    """
    Convert each DQI status string into a more detailed dict.

    :param errors: a list of error names
    :return: a list of dicts of information about each error
    """
    if not errors:
        return []
    # do an in check to make sure that we don't break if the error is one we just haven't mapped yet
    return [
        GBIF_ERRORS[error_code] for error_code in errors if error_code in GBIF_ERRORS
    ]


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
    Loop through all the classification parts, building an array of parts.

    :param gbif_record: return:
    """
    classification = []

    url = 'http://www.gbif.org/species'
    for classification_part in [
        'kingdom',
        'phylum',
        'class',
        'taxonorder',
        'family',
        'genus',
    ]:
        key = f'{classification_part}Key'
        key_value = gbif_record.get(key, None)
        name = gbif_record.get(classification_part, None)
        if key_value:
            classification.append(
                f'<a href="{url}/{key_value}" target="_blank" rel="nofollow">{name}</a>'
            )
        elif name:
            classification.append(name)

    return literal(' <i class="fa fa-angle-right"></i> '.join(classification))


def gbif_get_geography(occurrence):
    '''
    :param occurrence:
    '''
    geography = []
    for geographic_part in ['continent', 'country', 'stateprovince']:
        value = occurrence.get(geographic_part, None)

        if value:
            geography.append(value.replace('_', ' '))

    return literal(' <i class="icon-angle-right"></i> '.join(geography))


def gbif_render_datetime(date_str):
    """
    Render a GBIF formatted datetime.

    :param date_str: return:
    """
    return dateutil.parser.parse(date_str).strftime('%B %d, %Y')


def get_gbif_record_url(pkg, res, rec):
    """
    Given details about a combination of package, resource and record, return the GBIF
    view URL created from them.

    :param pkg: the package dict
    :param res: the resource dict
    :param rec: the record dict
    :return: the link to the GBIF view for this record/resource/package combo
    """
    # return the url for package/resource/record combo requested
    return toolkit.url_for(
        'gbif.view',
        package_name=pkg['name'],
        resource_id=res['id'],
        record_id=rec['_id'],
    )


def build_gbif_nav_item(package_name, resource_id, record_id, version=None):
    """
    Creates the gbif specimen nav item allowing the user to navigate to the gbif views
    of the specimen record data. A single nav item is returned.

    :param package_name: the package name (or id)
    :param resource_id: the resource id
    :param record_id: the record id
    :param version: the version of the record, or None if no version is present
    :return: a nav items
    """
    kwargs = {
        'package_name': package_name,
        'resource_id': resource_id,
        'record_id': record_id,
    }
    # if there's a version, add it to the kwargs
    if version is not None:
        kwargs['version'] = version
    # build the nav and return it
    return toolkit.h.build_nav_icon('gbif.view', toolkit._('GBIF view'), **kwargs)
