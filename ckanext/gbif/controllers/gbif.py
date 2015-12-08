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
    """
    Controller for displaying about pages
    """
    def view(self, package_name, resource_id, record_id):

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(context, {'id': resource_id})
            c.package = get_action('package_show')(context, {'id': package_name})
            c.pkg_dict = c.package
            record = get_action('record_show')(context, {'resource_id': resource_id, 'record_id': record_id})
            c.record_dict = record['data']

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        occurrence_id = c.record_dict.get('occurrenceID')

        if not occurrence_id:
            abort(404, _('GBIF record not found'))

        # And get the GBIF record
        try:
            gbif_record = tk.get_action('gbif_record_show')(context, {
                'occurrence_id': occurrence_id
            })
        except NotFound:
            abort(404, _('GBIF record not found'))
        else:
            return render('record/gbif.html', {
                'title': 'GBIF',
                'gbif_record': gbif_record,
                'organisation_key': pylons.config['ckanext.gbif.organisation_key'],
                'dataset_key': pylons.config['ckanext.gbif.dataset_key']
            })