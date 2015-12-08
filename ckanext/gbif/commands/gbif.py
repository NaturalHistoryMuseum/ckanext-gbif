
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
from sqlalchemy.exc import StatementError

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError


GBIF_ARCHIVE = '/Users/bens3/Downloads/0017401-151016162008034.zip'
BATCH_SIZE = 10000

# FIXME: publishingOrgKey missing

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
    uuid_field_name = 'occurrenceID'
    # The GBIF field names we want to keep
    field_names = [
        # GBIF data
        'gbifID',
        'occurrenceID', 'lastInterpreted', 'lastParsed',
        'issue',
        # Classification
        'kingdom', 'kingdomKey', 'phylum', 'phylumKey', 'class', 'classKey', 'order', 'orderKey', 'family', 'familyKey', 'genus', 'genusKey', 'subgenus', 'subgenusKey', 'species', 'speciesKey', 'taxonRank',
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
            self.load_dataset()
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
            print 'Creating schema %s' % self.pg_schema
            self.connection.execute('CREATE SCHEMA %s' % self.pg_schema)
            # FIXME
            # self.connection.execute('GRANT ALL ON SCHEMA foo TO staff' % self.pg_schema)

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
        # Grant access
        self.connection.execute('GRANT USAGE ON SCHEMA {schema} TO {table}'.format(
            schema=self.pg_schema,
            table=self.pg_table
        ))
        self.connection.execute('GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {table}'.format(
            schema=self.pg_schema,
            table=self.pg_table
        ))

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

    def simplify_occurrences_csv(self):
        """
        Create a simplified CSV of occurrences data
        The data from GBIF isn't usable if it contains JSON data with quotes
        Which our dynamicProperties have, and which breaks copy to postgres
        :return:
        """
        zip_file = zipfile.ZipFile(GBIF_ARCHIVE)
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
                    # TODO: Parsing CSV is mising up fields if they have a tab in them
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
                    count+=BATCH_SIZE
                    print count


    def copy_occurrences_csv_to_db(self):
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

    def load_dataset(self):
        """
        Load the GBIF Dataset

        Request data

        :return:
        """

        # TODO:
        # resource_id = pylons.config['ckanext.gbif.resource_id']
        # resource = tk.get_action('resource_show')(self.context, {'id': resource_id})

        # FIXME - Not working
        # api = GBIFAPI()
        # response = api.request_download(pylons.config['ckanext.gbif.dataset_key'])

        # self.simplify_occurrences_csv()
        # self.copy_occurrences_csv_to_db()
        self._index_gbif_table()