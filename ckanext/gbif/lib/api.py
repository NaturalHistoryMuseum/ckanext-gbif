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
    def _request(path, params):

        endpoint = os.path.join(GBIF_ENDPOINT, path)
        auth = (pylons.config['ckanext.gbif.username'], pylons.config['ckanext.gbif.password'])
        r = requests.get(endpoint, auth=auth, params=params)

        # Raise exception if we have an error
        r.raise_for_status()

        # Return the result
        return r.json()

    def occurrence_search(self, params):

        # /occurrence/search

        # Get the Dataset first
        # tk.get_action('datastore_delete')(self.context, {'resource_id': resource['id'], 'force': True})

        # lastInterpreted


        print pylons.config['ckanext.gbif.dataset_key']


    # def list_occurrence_datasets(self):
    #
    #     params = {
    #         'type': 'OCCURRENCE'
    #     }
    #
    #     return self._request('dataset', params)



    # def get_occurrences_in_area(self, geom):
    #
    #     limit = 300;
    #     offset = 0
    #
    #     scientific_names = [
    #         'Plecotus auritus',
    #         'Pipistrellus pipistrellus',
    #         'Myotis daubentoni',
    #         'Nyctalus leisleri',
    #         'Pipistrellus nathusii',
    #         'Myotis nattereri',
    #         'Nyctalus noctula',
    #         'Eptesicus serotinus',
    #         'Pipistrellus pygmaeus',
    #         'Myotis mystacinus',
    #         'Myotis brandtii',
    #     ]
    #
    #     params = {
    #         'geometry': geom,
    #         'hasCoordinate': True,
    #         'limit': limit,
    #     }
    #
    #     with open('/vagrant/london-bats.csv', 'wb') as f:
    #
    #         csv_writer = csv.writer(f)
    #
    #         for name in scientific_names:
    #
    #             print 'STARTING: %s' % name
    #
    #             params['scientificName'] = name
    #
    #             genus = name.split(' ')[0]
    #
    #             # Reset offset
    #             offset = 0
    #
    #             while True:
    #
    #                 print 'Retrieving %s' % offset
    #
    #                 params['offset'] = offset
    #
    #                 try:
    #                     response = self._request('occurrence/search', params)
    #                 except requests.exceptions.ConnectionError:
    #                     pass
    #                 else:
    #
    #                     print 'Count: ', response.get('count', 0)
    #
    #                     for record in response['results']:
    #
    #                         date = []
    #                         for date_part in ['year', 'month', 'day']:
    #                             try:
    #                                 date.append(str(record[date_part]))
    #                             except KeyError:
    #                                 date.append('01')
    #
    #                         date_str = '-'.join(date)
    #
    #                         csv_writer.writerow([
    #                             record[u'scientificName'],
    #                             record[u'decimalLatitude'],
    #                             record[u'decimalLongitude'],
    #                             date_str,
    #                             genus
    #
    #                         ])
    #
    #                 offset += limit
    #
    #                 if response['endOfRecords']:
    #                     print 'END'
    #                     break
    #
    #



                # for record in response['results']:
                #

                #
                # print offset

    # def download(self):
    #
    #     params = {
    #         'notification_address': ['ben@bencott.co.uk'],
    #         "predicate": {
    #             'type': "within",
    #             "geometry": 'POLYGON ((-0.3790283203125 51.32374658474385, 0.1922607421875 51.30657945585936, 0.2801513671875 51.58389660297626, 0.10986328125 51.70660846336452, -0.41748046875 51.730430542940184, -0.5438232421874999 51.587309751245456, -0.5328369140625 51.4163381064004, -0.3790283203125 51.32374658474385))'
    #         }
    #     }
    #
    #     endpoint = os.path.join(GBIF_ENDPOINT, 'occurrence/download/request')
    #     r = requests.post(endpoint, auth=(config.get('gbif', 'username'), config.get('gbif', 'password')), params=params)
    #     r.raise_for_status()
    #
    #     print r






#
#
#
#
#
#
# class GBIFDatasetAPI(GBIFAPI):
#     path = 'dataset'
#
#     def list_occurrence_datasets(self, **kwargs):
#         kwargs['type'] = 'OCCURRENCE'
#
#
#         print response['count']
#
#         # for result in response['results']:
#         #     print result['key']
#         #     print result['title']
#

# class GBIFOccurrenceAPI(GBIFAPI):
#     path = 'occurrence'
#
#
#
#     def search(self, **kwargs):
#         """
#         Perform a search - add search to path
#         @param kwargs:
#         @return:
#         """
#         return self.request(path='search', **kwargs)
#
#     def get_issue(self, key, issue):
#
#         assert issue in self.issues
#
#         response = self.search(params={'datasetKey': key, 'issue': issue})
#
#         print issue, response['count']
#
#         # if response['count']:
#         #     print response
#
#     def get_issue_counts(self, key):
#         """
#         Return a list of all dataset issues counts
#         @param key: dataset key
#         @return:
#         """
#
#         for issue in self.issues:
#             self.get_issue(key, issue)

