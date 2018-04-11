#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

import pylons
import logging
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class GBIFController(p.toolkit.BaseController):
    '''Controller for displaying about pages'''
    def view(self, package_name, resource_id, record_id):
        '''

        :param package_name: 
        :param resource_id: 
        :param record_id: 

        '''

        context = {u'model': model, u'session': model.Session, u'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action(u'resource_show')(context, {u'id': resource_id})
            c.package = get_action(u'package_show')(context, {u'id': package_name})
            c.pkg_dict = c.package
            record = get_action(u'record_show')(context, {u'resource_id': resource_id, u'record_id': record_id})
            c.record_dict = record[u'data']

        except NotFound:
            abort(404, _(u'Resource not found'))
        except NotAuthorized:
            abort(401, _(u'Unauthorized to read resource %s') % package_name)

        occurrence_id = c.record_dict.get(u'occurrenceID')

        if not occurrence_id:
            abort(404, _(u'GBIF record not found'))

        # And get the GBIF record
        try:
            gbif_record = tk.get_action(u'gbif_record_show')(context, {
                u'occurrence_id': occurrence_id
            })
        except NotFound:
            abort(404, _(u'GBIF record not found'))
        else:
            return render(u'record/gbif.html', {
                u'title': u'GBIF',
                u'gbif_record': gbif_record,
                u'organisation_key': pylons.config[u'ckanext.gbif.organisation_key'],
                u'dataset_key': pylons.config[u'ckanext.gbif.dataset_key']
            })
