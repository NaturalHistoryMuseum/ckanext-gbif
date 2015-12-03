#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import requests
import pylons
from pylons import config

GBIF_ENDPOINT = 'http://api.gbif.org/v1'


class GBIFAPI():

    def __init__(self):
        self.auth = (config['ckanext.gbif.username'], config['ckanext.gbif.password'])

    def request_download(self, dataset_key):
        path = '/occurrence/download/request'
        params = {
            "creator": config['ckanext.gbif.username'],
            "notification_address": ["ben@benscott.co.uk"],
            "predicate":
                {
                    "type": "equals",
                    "key": "datasetKey",
                    "value": dataset_key
                }
        }

        r = requests.post(GBIF_ENDPOINT + path, json=params, auth=self.auth)
        r.raise_for_status()

        # Return the result
        return r.json()

