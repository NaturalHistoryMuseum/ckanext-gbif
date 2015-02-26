import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
from ckan.plugins import toolkit as tk
from requests import HTTPError
from ckanext.gbif.lib.api import GBIFAPI
import logging

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
            record = get_action('record_get')(context, {'resource_id': resource_id, 'record_id': record_id})
            c.record_dict = record['data']

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        occurrence_id = c.record_dict.get('occurrenceID')

        # Load the gbif_id (it's a hidden field so we need to manually add it
        sql = """SELECT _gbif_id FROM "{resource_id}" WHERE "occurrenceID"='{occurrence_id}'""".format(
            resource_id=c.resource['id'],
            occurrence_id=occurrence_id
        )

        try:
            result = tk.get_action('datastore_search_sql')(context, {'sql': sql})
            gbif_id = result['records'][0]['_gbif_id']
        except (ValidationError, IndexError):
            abort(404, _('GBIF record not found'))

        try:
            api = GBIFAPI()
            occurrence = api.get_occurrence(gbif_id)
        except HTTPError:
            abort(404, _('GBIF record not found'))

        return render('record/gbif.html', {
            'title': 'GBIF',
            'occurrence': occurrence
        })