
import logging
import pylons
import ckan.logic as logic
import zipfile
import csv
from ckan.plugins import toolkit as tk
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
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

        paster gbif-api update-errors -c /etc/ckan/default/development.ini

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

        count = 0

        zip_file = zipfile.ZipFile(self.options.file_path)
        with zip_file.open('occurrence.txt') as f:

            update_values = list()

            sql = """
                UPDATE "{resource_id}"
                AS r
                SET "_gbif_id" = v."_gbif_id"
                FROM (VALUES {update_values}) as v("occurrenceID", _gbif_id)
                WHERE r."occurrenceID" = v."occurrenceID"::uuid;
            """

            update_values.append("('%s', %s)" % ('03ce209a-2164-498e-a5f6-a54534bd4165', 123))

            for row in csv.DictReader(f, delimiter='\t'):

                count+=1

                # print row.keys()
                errors = row['issue'].split(';') if row['issue'] else None
                update_values.append("('%s', %s)" % (row['occurrenceID'], int(row['gbifID'])))

                # FIXME: Some records coming from GBIF are missing the OccurrenceID field
                # This seems to be when the habitat field is populated (and contains a tab?)
                if not row['occurrenceID']:
                    continue
                    print 'Missing occurrence ID'

                if count > 10000:
                    connection = self.engine.connect()
                    result = connection.execute(sql.format(
                        resource_id=pylons.config['ckanext.gbif.resource_id'],
                        update_values=','.join(update_values))
                    )

                    print count
                    return
