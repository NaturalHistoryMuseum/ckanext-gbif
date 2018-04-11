#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import pylons
import ckan.logic as logic
from ckanext.datastore.db import _get_engine
from ckanext.datastore.db import _execute_single_statement

_get_or_bust = logic.get_or_bust
NotFound = logic.NotFound


def gbif_record_show(context, data_dict):
    '''Update the DQI of a record based on a list of GBIF errors

    :param context: CKAN context
    :param data_dict: Action parameters:
        - occurrence_id

    '''
    occurrence_id = _get_or_bust(data_dict, u'occurrence_id')
    # Set up DB connection to datastore
    context[u'connection'] = _get_engine({u'connection_url': pylons.config[u'ckan.datastore.read_url']}).connect()
    sql = u'SELECT * FROM gbif WHERE occurrenceid=%s LIMIT 1'
    result = _execute_single_statement(context, sql, occurrence_id)
    record = result.fetchone()
    if record:
        return dict(record)
    else:
        raise NotFound
