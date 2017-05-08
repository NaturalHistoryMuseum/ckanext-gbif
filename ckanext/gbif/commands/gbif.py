import os
import time
import glob
import logging, logging.handlers
import pylons
import ckan.logic as logic
import zipfile
import csv
from ckan.plugins import toolkit as tk
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
from uuid import UUID
from ckanext.gbif.lib.api import GBIFAPI
from sqlalchemy.exc import StatementError
import ckan.lib.mailer as mailer
from dateutil import parser
import datetime
import pytz

log = logging.getLogger()

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

BATCH_SIZE = 10000


class GBIFCommand(CkanCommand):
    """

    GBIF API Commands

    Commands:

        paster gbif load-dataset -c /etc/ckan/default/development.ini
        paster gbif load-dataset -c /Users/bens3/Projects/NaturalHistoryMuseum/DataPortal/ckan/etc/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    pg_schema = 'gbif'
    pg_table = 'occurrence'
    last_runtime_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.log')
    uuid_field_name = 'occurrenceID'
    # The GBIF field names we want to keep
    field_names = [
        # GBIF data
        'gbifID',
        'occurrenceID', 'lastInterpreted', 'lastParsed',
        'issue',
        # Classification
        'kingdom', 'kingdomKey', 'phylum', 'phylumKey', 'class', 'classKey', 'order', 'orderKey', 'family', 'familyKey', 'genus', 'genusKey', 'subgenus', 'subgenusKey', 'species', 'speciesKey',
        'taxonRank',
        # Identification
        'identifiedBy', 'scientificName', 'taxonKey',
        # Collection event
        'recordedBy', 'eventDate', 'recordNumber',
        # Geography
        'continent', 'country', 'stateProvince',
        # Location
        'habitat', 'countryCode', 'islandGroup', 'decimalLongitude', 'decimalLatitude'
    ]

    # Temporary outfile for writing CSV
    outfile = '/tmp/gbif.csv'

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up datastore DB engine
        self.engine = _get_engine({
            'connection_url': pylons.config['ckan.datastore.write_url']
        })

        self.connection = self.engine.connect()

        # Set up context
        user = tk.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}
        cmd = self.args[0]
        if cmd == 'load-dataset':
            self._create_gbif_table()
            print('Load')
            self.load_dataset()
        elif cmd == 'create-table':
            self._create_gbif_table()
        else:
            print 'Command %s not recognized' % cmd

    def _create_gbif_table(self):
        """
        Make sure the GBIF
        :return:
        """
        # Check schema

        schema_exists = self.connection.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = '%s'" % self.pg_schema).scalar()
        if not schema_exists:
            raise Exception('Schema %s does not exist' % self.pg_schema)

        # Drop table if it exists
        self.connection.execute('DROP TABLE IF EXISTS {schema}.{table}'.format(
            schema=self.pg_schema,
            table=self.pg_table
        ))
        # And recreate the table
        print 'Creating table %s.%s' % (self.pg_schema, self.pg_table)

        columns = []
        for fn in self.field_names:
            col = self._get_column_name(fn)
            if fn == self.uuid_field_name:
                columns.append('"%s" uuid NOT NULL' % col)
            else:
                columns.append('"%s" text DEFAULT NULL' % col)

        sql = "CREATE TABLE {schema}.{table} ({columns})".format(
            schema=self.pg_schema,
            table=self.pg_table,
            columns=', '.join(columns),
        )
        self.connection.execute(sql)

    @staticmethod
    def _get_column_name(field_name):
        """
        To avoid collisions with datastore columns
        Prefix field names with 'GBIF'
        :return:
        """
        # If this already starts with gbif (e.g. gbifID) ignore it
        if field_name[0:4] == 'gbif':
            return field_name
        else:
            return 'gbif' + field_name[0].upper() + field_name[1:]

    def _index_gbif_table(self):
        """
        For faster loading, we only add the index after records have been added
        :return:
        """

        col = self._get_column_name(self.uuid_field_name)

        print 'Creating index on %s' % col
        sql = 'ALTER TABLE {schema}.{table} ADD PRIMARY KEY ("{col}")'.format(
            schema=self.pg_schema,
            table=self.pg_table,
            col=col
        )
        self.connection.execute(sql)

    def _simplify_occurrences_csv(self, gbif_archive_file):
        """
        Create a simplified CSV of occurrences data
        The data from GBIF isn't usable if it contains JSON data with quotes
        Which our dynamicProperties have, and which breaks copy to postgres
        :return:
        """

        if not os.path.isfile(gbif_archive_file):
            raise IOError('GBIF archive does not exist: %s' % gbif_archive_file)
        zip_file = zipfile.ZipFile(gbif_archive_file)
        count = 0
        with zip_file.open('occurrence.txt') as f:
            csv_reader = csv.DictReader(f, delimiter='\t')
            csv_writer = csv.writer(open(self.outfile, 'wb'))
            # Add headers
            headers = [self._get_column_name(fn) for fn in self.field_names]
            csv_writer.writerow(headers)
            output = []
            for row in csv_reader:
                uuid = row.get(self.uuid_field_name, None)
                # Ensure we have a valid UUID for this record
                if not uuid:
                    print 'Skipping: no UUID'
                    continue
                else:
                    # Ensure the Occurrence ID is a valid UUID
                    # TODO: Parsing CSV is messing up fields if they have a tab in them
                    try:
                        UUID(row[self.uuid_field_name], version=4)
                    except ValueError:
                        print 'Skipping: not a valid UUID'
                        # Value error - not a valid hex code for a UUID.
                        continue

                output.append([row.get(k) for k in self.field_names])
                if len(output) > BATCH_SIZE:
                    csv_writer.writerows(output)
                    output = []
                    count += BATCH_SIZE
                    print count

    def _copy_occurrences_csv_to_db(self):
        """
        Copy the simplified CSV file to postgres
        :return:
        """
        self._create_gbif_table()
        conn = self.engine.raw_connection()
        cursor = conn.cursor()
        table = '%s.%s' % (self.pg_schema, self.pg_table)
        sql = "COPY %s FROM STDIN WITH CSV HEADER DELIMITER AS ','" % table
        print 'Copying CSV file to %s' % table
        with open(self.outfile) as f:
            cursor.copy_expert(sql=sql, file=f)
            conn.commit()

    def _error_notification(self, err):
        """
        Send email notification that an action is required
        :return:
        """

        body = '{0}\n\nMany thanks,\nData Portal Bot'.format(err)

        mail_dict = {
            'recipient_email': pylons.config.get('email_to'),
            'recipient_name': pylons.config.get('ckanext.contact.recipient_name') or pylons.config.get('ckan.site_title'),
            'sender_name': pylons.config.get('ckan.site_title'),
            'sender_url': pylons.config.get('ckan.site_url'),
            'subject': 'GBIF Import Error',
            'body': body,
            'headers': {'reply-to': 'no-reply'}
        }

        mailer._mail_recipient(**mail_dict)

    def _get_last_runtime(self):
        """
        Get timestamp of last import
        :return:
        """
        try:
            with open(self.last_runtime_file, 'r') as f:
                runtime = f.readline()
                return float(runtime)
        except IOError:
            # If the file doesn't exist, last runtime is None
            return None

    def _set_last_runtime(self, runtime):
        """
       Set timestamp of last import (using the file ctime)
        :return:
        """
        with open(self.last_runtime_file, 'w') as f:
            f.write(str(runtime))

    def load_dataset(self):
        """
        Loads the GBIF Dataset into the CKAN Datastore

        :return:
        """

        print('Running GBIF:Load dataset')

        gbif_dataset_uuid = pylons.config['ckanext.gbif.dataset_key']
        archive_dir = pylons.config['ckanext.gbif.import_dir']

        # Get the current GBIF ID
        api = GBIFAPI()
        dataset = api.get_dataset(gbif_dataset_uuid)

        # Get the date the last dataset was published
        dataset_published_date = parser.parse(dataset['pubDate'])

        # Get the last time the GBIF import was run
        last_runtime = self._get_last_runtime()

        # If the GBIF published date isn't more recent than the last runtime
        # There is no need to re-import
        if last_runtime and dataset_published_date < datetime.datetime.fromtimestamp(last_runtime, pytz.UTC):
            print('GBIF dataset has not been updated since last run. Exiting')
            return

        # Try and file potential GBIF import files
        files = glob.glob(os.path.join(archive_dir, '*-*.zip'))

        # We do not have a GBIF dump file to import
        if not files:
            log.error('No GBIF export file to import')
            err = """
            There is no GBIF export file to import.

            Please download a new export of Natural History Records from GBIF (http://www.gbif.org/occurrence/search?datasetKey={gbif_dataset_uuid}) and upload it to {archive_dir}.

            """.format(
                gbif_dataset_uuid=gbif_dataset_uuid,
                archive_dir=archive_dir
            )

            self._error_notification(err)
            return

        # Ensure we're using the newest file
        newest_file = max(files, key=os.path.getctime)
        ctime = os.path.getctime(newest_file)

        # If the newest file is the last one processed, see if we have a more recent GBIF dataset to download
        if ctime == last_runtime and dataset_published_date > datetime.datetime.fromtimestamp(last_runtime, pytz.UTC):
            log.error('Newer version of GBIF data to import. Please download from GBIF.')
            err = """
            There is newer version of GBIF data to import.

            The most recent available import file ({newest_file}) was created on {newest_file_ts}.
            The NHM dataset on GBIF was updated on {dataset_published_date}.

            Please download a new export of Natural History Records from GBIF (http://www.gbif.org/occurrence/search?datasetKey={gbif_dataset_uuid}) and upload it to {archive_dir}/.

            """.format(
                newest_file=newest_file,
                newest_file_ts=datetime.datetime.fromtimestamp(ctime, pytz.UTC),
                dataset_published_date=dataset_published_date,
                gbif_dataset_uuid=gbif_dataset_uuid,
                archive_dir=archive_dir
            )

            self._error_notification(err)
            return

        # Process the file, importing into the Data Portal
        self._create_gbif_table()
        self._simplify_occurrences_csv(newest_file)
        self._copy_occurrences_csv_to_db()
        self._index_gbif_table()

        # ANd set the last runtime, so when run on cron
        self._set_last_runtime(ctime)
