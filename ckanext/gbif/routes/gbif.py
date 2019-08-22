# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

blueprint = Blueprint(name=u'gbif', import_name=__name__,
                      url_prefix='/dataset/<package_name>/resource/<resource_id>/record'
                                 '/<record_id>/gbif')


@blueprint.route('', defaults={u'version': None})
@blueprint.route('/<int:version>')
def view(package_name, resource_id, record_id, version=None):
    context = {
        u'user': toolkit.c.user or toolkit.c.author
        }

    # Try & get the resource
    try:
        toolkit.c.resource = toolkit.get_action(u'resource_show')(context, {
            u'id': resource_id
            })
        toolkit.c.package = toolkit.get_action(u'package_show')(context, {
            u'id': package_name
            })
        toolkit.c.pkg_dict = toolkit.c.package

        record_data_dict = {
            u'resource_id': resource_id,
            u'record_id': record_id
            }
        if version is not None:
            version = int(version)
            record_data_dict[u'version'] = version
        toolkit.c.version = version
        record = toolkit.get_action(u'record_show')(context, record_data_dict)
        toolkit.c.record_dict = record[u'data']
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._(u'Resource not found'))
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._(u'Unauthorized to read resource %s') % package_name)

    gbif_id = toolkit.c.record_dict.get(u'gbifID', None)
    if gbif_id is None:
        toolkit.abort(404, toolkit._(u'GBIF record not found'))

    # And get the GBIF record
    try:
        gbif_record = toolkit.get_action(u'gbif_record_show')(context, {
            u'gbif_id': gbif_id
            })
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._(u'GBIF record not found'))
    else:
        return toolkit.render(u'record/gbif.html', {
            u'title': u'GBIF',
            u'gbif_record': gbif_record,
            u'organisation_key': toolkit.config[u'ckanext.gbif.organisation_key'],
            u'dataset_key': toolkit.config[u'ckanext.gbif.dataset_key']
            })
