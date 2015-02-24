
import logging
import pylons
import ckan.logic as logic
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
import pylons
from ckanext.gbif.lib.api import GBIFAPI

log = logging.getLogger()

class GBIFCommand(CkanCommand):
    """

    GBIF API COmmands

    Commands:

        paster gbif-api update-errors -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # # Set up context
        # user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        # self.context = {'user': user['name']}
        #
        # # Set up datastore DB engine
        # self.engine = _get_engine({
        #     'connection_url': pylons.config['ckan.datastore.write_url']
        # })

        cmd = self.args[0]

        if cmd == 'update-errors':
            self.update_errors()
        else:
            print 'Command %s not recognized' % cmd


    def update_errors(self):

        # TODO: Loop through the records without errors


        api = GBIFAPI()
        api.get_dataset_errors()
