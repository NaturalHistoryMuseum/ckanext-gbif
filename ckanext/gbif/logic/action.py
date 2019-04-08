import requests

import ckan.logic as logic

_get_or_bust = logic.get_or_bust
NotFound = logic.NotFound


def gbif_record_show(context, data_dict):
    """
    Retrieve a GBIF record with the given GBIF ID. This is done via the GBIF API.

    :param context: CKAN context
    :param data_dict: dict of parameters, only one is required: gbif_id
    """
    gbif_id = _get_or_bust(data_dict, u'gbif_id')
    response = requests.get(u'https://api.gbif.org/v1/occurrence/{}'.format(gbif_id))
    # if there was an error getting the record, raise a not found error
    if 400 <= response.status_code < 600:
        raise NotFound
    else:
        return response.json()
