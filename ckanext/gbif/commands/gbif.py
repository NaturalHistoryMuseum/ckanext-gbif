
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


log = logging.getLogger()

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

# BATCH_SIZE = 100  # Commit every x number of rows
# COMMIT_FROM = None  # If set, only commit past x number of rows (use if there's been an error)

GBIF_ARCHIVE = '/Users/bens3/Downloads/0017401-151016162008034.zip'
BATCH_SIZE = 10000

class GBIFCommand(CkanCommand):
    """

    GBIF API Commands

    Commands:

        paster gbif load-dataset -c /etc/ckan/default/development.ini

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
        'occurrenceID', 'lastInterpreted', 'lastParsed', 'publishingOrgKey', 'datasetKey',
        'issue',
        # Classification
        'kingdom', 'kingdomKey', 'phylum', 'phylumKey', 'class', 'classKey', 'order', 'orderKey', 'family', 'familyKey', 'genus', 'genusKey', 'species', 'speciesKey', 'taxonRank',
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

    # def update_errors(self):
    #
    #     gbif_dataset_key = pylons.config['ckanext.gbif.dataset_key']
    #     resource_id = pylons.config['ckanext.gbif.resource_id']
    #
    #     resource = tk.get_action('resource_show')(self.context, {'id': resource_id})
    #
    #     # Do we have any new/updated records? (dqi == Unknown)
    #     sql = """
    #       SELECT count(*) FROM "{resource_id}" WHERE dqi='{dqi}'
    #     """.format(resource_id=resource_id, dqi=UNKNOWN)
    #
    #     try:
    #         result = tk.get_action('datastore_search_sql')(self.context, {'sql': sql})
    #     except ValidationError, e:
    #         log.critical('Error retrieving last modified date %s', e)
    #     else:
    #
    #         count = int(result['records'][0][u'count'])
    #
    #         if count:
    #             print '%s records to update' % count
    #
    #             # 2015-02-24T14:15:30.053897
    #
    #         # If we have records, update
    #
    #             print resource['last_modified']
    #
    #         # print result

    def _ensure_gbif_table(self):
        """
        Make sure the GBIF
        :return:
        """
        # Check schema

        schema_exists = self.connection.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = '%s'" % self.pg_schema).scalar()
        if not schema_exists:
            print 'Creating schema %s' % self.pg_schema
            self.connection.execute('CREATE SCHEMA %s' % self.pg_schema)

        # Drop table if it exists
        self.connection.execute('DROP TABLE IF EXISTS {schema}.{table}'.format(
            schema=self.pg_schema,
            table=self.pg_table
        ))
        # And recreate the table
        print 'Creating table %s.%s' % (self.pg_schema, self.pg_table)
        sql = "CREATE TABLE {schema}.{table} ({columns})".format(
            schema=self.pg_schema,
            table=self.pg_table,
            columns=', '.join(['"%s" text DEFAULT NULL' % f for f in self.field_names]),
        )
        self.connection.execute(sql)

    def _index_gbif_table(self):
        """
        For faster loading, we only add the index after records have been added
        :return:
        """
        print 'Creating index on %s' % self.uuid_field_name
        sql = 'ALTER TABLE {schema}.{table} ADD PRIMARY KEY ("{uuid_field_name}")'.format(
            schema=self.pg_schema,
            table=self.pg_table,
            uuid_field_name=self.uuid_field_name
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
            csv_writer.writerow(self.field_names)
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
        self._ensure_gbif_table()
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

        self.simplify_occurrences_csv()
        self.copy_occurrences_csv_to_db()
        self._index_gbif_table()





        #
        #
            # fieldnames = reader.fieldnames
            # print fieldnames
        #     fieldnames.remove('dynamicProperties')
        #
        #     print outfile


            # # Create the table
            # self._ensure_gbif_table(fieldnames)
            # # And load the data
            #
            # sql = "COPY %s FROM STDIN WITH CSV HEADER DELIMITER AS '\t'"
            #
            # cursor.copy_expert(sql=sql % table, file=f)

            # return

            # print 'Copying occurrence data to %s' % table
            # records = []
            # count = 0
            # for row in reader:
            #     records.append(row)
            #     if len(records) > BATCH_SIZE:
            #
            #         sql = 'INSERT INTO {table}({cols}) VALUES ({values})'.format(
            #                 table=table,
            #                 cols=', '.join(['"%s"' % k for k, v in row.items() if v]),
            #                 values=', '.join(['"%s"' % v for v in row.values() if v])
            #             )
            #
            #         print sql

                    # try:
                    #     self.connection.execute(sql, records)
                    # except StatementError, e:
                    #     # print 'ERROR'
                    #     raise
                    # else:
                    #     count += BATCH_SIZE
                    #     print "Inserted %s" % count
                    #     records = []



            #
            #     print sql



            #     print row['occurrenceID']
            #     print row['issue'].split(';') if row['issue'] else []





    # def load_errors_from_file(self):
    #     """
    #     Load errors from a GBIF dataset download
    #     @return:
    #     """
    #     if not self.options.file_path:
    #         raise self.BadCommand('No filepath supplied')
    #
    #     resource_id = pylons.config['ckanext.gbif.resource_id']
    #     zip_file = zipfile.ZipFile(self.options.file_path)
    #
    #     total = 0
    #
    #     with zip_file.open('occurrence.txt') as f:
    #
    #         # Build a list of records
    #         records = list()
    #
    #         for row in csv.DictReader(f, delimiter='\t'):
    #
    #             # FIXME: Some records coming from GBIF are missing the OccurrenceID field
    #             # This seems to be when the habitat field is populated (and contains a tab?)
    #             if not row['occurrenceID']:
    #                 continue
    #                 print 'Missing occurrence ID'
    #

    #
    #             records.append({
    #                 'occurrence_id': row['occurrenceID'],
    #                 'errors': row['issue'].split(';') if row['issue'] else [],
    #                 'gbif_id': row['gbifID']
    #             })
    #
    #             # Commit every 10000 rows
    #             if len(records) > BATCH_SIZE:
    #
    #                 if not COMMIT_FROM or total > COMMIT_FROM:
    #                     print "Updating datastore"
    #                     tk.get_action('update_record_dqi')(self.context, {'resource_id': resource_id, 'records': records})
    #
    #                 # And reset the list
    #                 records = list()
    #
    #                 total += BATCH_SIZE
    #                 print total
    #
    #         # If we have any remaining records, save them
    #         if records:
    #             tk.get_action('update_record_dqi')(self.context, {'resource_id': resource_id, 'records': records})