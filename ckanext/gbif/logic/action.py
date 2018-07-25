#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

from ckanext.datastore import backend as datastore_db

from ckan.plugins import toolkit


def gbif_record_show(context, data_dict):
    '''Update the DQI of a record based on a list of GBIF errors

    :param context: CKAN context
    :param data_dict: Action parameters:
        - occurrence_id

    '''
    occurrence_id = toolkit.get_or_bust(data_dict, u'occurrence_id')
    # Set up DB connection to datastore
    context[u'connection'] = datastore_db._get_engine({
        u'connection_url': toolkit.config[
            u'ckan.datastore.read_url']
        }).connect()
    sql = u'SELECT * FROM gbif WHERE occurrenceid=%s LIMIT 1'
    result = datastore_db._execute_single_statement(context, sql, occurrence_id)
    record = result.fetchone()
    if record:
        return dict(record)
    else:
        raise toolkit.ObjectNotFound
