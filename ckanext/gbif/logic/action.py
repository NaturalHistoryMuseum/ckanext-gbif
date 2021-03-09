#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import requests

from ckan.plugins import toolkit


def gbif_record_show(context, data_dict):
    """
    Retrieve a GBIF record with the given GBIF ID. This is done via the GBIF API.

    :param context: CKAN context
    :param data_dict: dict of parameters, only one is required: gbif_id
    """
    gbif_id = toolkit.get_or_bust(data_dict, 'gbif_id')
    response = requests.get(f'https://api.gbif.org/v1/occurrence/{gbif_id}')
    # if there was an error getting the record, raise a not found error
    if 400 <= response.status_code < 600:
        raise toolkit.ObjectNotFound
    else:
        return response.json()
