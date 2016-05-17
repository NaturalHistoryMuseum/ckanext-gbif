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

    def get_dataset(self, uuid):
        url = os.path.join(GBIF_ENDPOINT, 'dataset', uuid)
        r = requests.get(url)
        r.raise_for_status()
        return r.json()


