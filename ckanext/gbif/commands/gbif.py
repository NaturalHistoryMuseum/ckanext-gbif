
import logging
import pylons
import ckan.logic as logic
import zipfile
import csv
from ckan.plugins import toolkit as tk
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
from uuid import UUID
from ckanext.gbif.lib.api import GBIFAPI


log = logging.getLogger()

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

UNKNOWN = 'Unknown'

class GBIFCommand(CkanCommand):
    """

    GBIF API COmmands

    Commands:

        paster gbif-api load-errors -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up datastore DB engine
        self.engine = _get_engine({
            'connection_url': pylons.config['ckan.datastore.write_url']
        })

        # Set up context
        user = tk.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        cmd = self.args[0]

        if cmd == 'update-errors':
            self.update_errors()
        elif cmd == 'load-errors':
            self.load_errors_from_file()
        else:
            print 'Command %s not recognized' % cmd

    def update_errors(self):

        gbif_dataset_key = pylons.config['ckanext.gbif.dataset_key']
        resource_id = pylons.config['ckanext.gbif.resource_id']

        resource = tk.get_action('resource_show')(self.context, {'id': resource_id})

        # Do we have any new/updated records? (dqi == Unknown)
        sql = """
          SELECT count(*) FROM "{resource_id}" WHERE dqi='{dqi}'
        """.format(resource_id=resource_id, dqi=UNKNOWN)

        try:
            result = tk.get_action('datastore_search_sql')(self.context, {'sql': sql})
        except ValidationError, e:
            log.critical('Error retrieving last modified date %s', e)
        else:

            count = int(result['records'][0][u'count'])

            if count:
                print '%s records to update' % count

                # 2015-02-24T14:15:30.053897

            # If we have records, update

                print resource['last_modified']

            # print result

    def load_errors_from_file(self):
        """
        Load errors from a GBIF dataset download
        @return:
        """
        if not self.options.file_path:
            raise self.BadCommand('No filepath supplied')

        resource_id = pylons.config['ckanext.gbif.resource_id']
        zip_file = zipfile.ZipFile(self.options.file_path)

        batch_size = 10000
        total = 0

        with zip_file.open('occurrence.txt') as f:

            # Build a list of records
            records = list()

            for row in csv.DictReader(f, delimiter='\t'):

                # FIXME: Some records coming from GBIF are missing the OccurrenceID field
                # This seems to be when the habitat field is populated (and contains a tab?)
                if not row['occurrenceID']:
                    continue
                    print 'Missing occurrence ID'

                # Ensure the Occurrence ID is valid
                # TODO: Parsing CSV is mixing up fields
                try:
                    UUID(row['occurrenceID'], version=4)
                except ValueError:
                    # Value error - not a valid hex code for a UUID.
                    continue

                records.append({
                    'occurrence_id': row['occurrenceID'],
                    'errors': row['issue'].split(';') if row['issue'] else [],
                    'gbif_id': row['gbifID']
                })

                # Commit every 10000 rows
                if len(records) > batch_size:
                    tk.get_action('update_record_dqi')(self.context, {'resource_id': resource_id, 'records': records})
                    # And reset the list
                    records = list()

                    total += batch_size
                    print total

            # If we have any remaining records, save them
            if records:
                tk.get_action('update_record_dqi')(self.context, {'resource_id': resource_id, 'records': records})