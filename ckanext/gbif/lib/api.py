#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import requests
import pylons


GBIF_ENDPOINT = 'http://api.gbif.org/v1'

class GBIFAPI(object):

    @staticmethod
    def _request(path, params={}):

        endpoint = os.path.join(GBIF_ENDPOINT, path)
        auth = (pylons.config['ckanext.gbif.username'], pylons.config['ckanext.gbif.password'])
        r = requests.get(endpoint, auth=auth, params=params, timeout=10)

        # Raise exception if we have an error
        r.raise_for_status()

        # Return the result
        return r.json()

    def get_occurrence(self, occurrence_id):
        return self._request('occurrence/%s' % occurrence_id)
