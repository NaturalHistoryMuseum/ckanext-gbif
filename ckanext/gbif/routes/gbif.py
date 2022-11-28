# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

blueprint = Blueprint(
    name='gbif',
    import_name=__name__,
    url_prefix='/dataset/<package_name>/resource/<resource_id>/record'
    '/<record_id>/gbif',
)


@blueprint.route('', defaults={'version': None})
@blueprint.route('/<int:version>')
def view(package_name, resource_id, record_id, version=None):
    context = {'user': toolkit.c.user or toolkit.c.author}

    # Try & get the resource
    try:
        toolkit.c.resource = toolkit.get_action('resource_show')(
            context, {'id': resource_id}
        )
        toolkit.c.package = toolkit.get_action('package_show')(
            context, {'id': package_name}
        )
        toolkit.c.pkg = context['package']
        toolkit.c.pkg_dict = toolkit.c.package

        record_data_dict = {'resource_id': resource_id, 'record_id': record_id}
        if version is not None:
            version = int(version)
            record_data_dict['version'] = version
        toolkit.c.version = version
        record = toolkit.get_action('record_show')(context, record_data_dict)
        toolkit.c.record_dict = record['data']
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._('Resource not found'))
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._('Unauthorized to read resource %s') % package_name)

    gbif_id = toolkit.c.record_dict.get('gbifID', None)
    if gbif_id is None:
        toolkit.abort(404, toolkit._('GBIF record not found'))

    # And get the GBIF record
    try:
        gbif_record = toolkit.get_action('gbif_record_show')(
            context, {'gbif_id': gbif_id}
        )
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._('GBIF record not found'))
    else:
        return toolkit.render(
            'record/gbif.html',
            {
                'title': 'GBIF',
                'gbif_record': gbif_record,
                'organisation_key': toolkit.config['ckanext.gbif.organisation_key'],
                'dataset_key': toolkit.config['ckanext.gbif.dataset_key'],
            },
        )
