# ckanext-gbif
GBIF Data Quality Indicators

Settings:

GBIF API username & password
ckanext.gbif.username = 
ckanext.gbif.password = 

TODO: How to do we associate local dataset ID with GBIF's?

## Prepare the database

There is currently no automatic schema/migration, so you need to manually prepare the database before using this plugin:

1. Create the dqi type:

```sql
CREATE TYPE dqi AS ENUM ('N/A', 'Unknown', 'Major errors', 'Minor errors', 'No errors');
```

2. Add the dqi field to the nhm specimen resource table:

```sql
 ALTER TABLE "..." ADD COLUMN "dqi" dqi DEFAULT 'Unknown';
 ```

## Use the API

You can update the status of a record by invoking the API endpoint at `update_record_dqi` and providing the following parameters:

- `resource_id`: The id of the resource you want to update (required);
- `filters`: A dictionary of filters defining the rows to update (required);
- `errors`: A list of GBIF errors (eg. ['TAXON_MATCH_NONE']) (required);
- `force`: If True, update read only resources (optional, defaults to False).

You will also need to provide the proper API key.

Internally:

```python
    from ckan.plugins import toolkit
    context = {}
    toolkit.get_action('update_record_dqi')(context, {
      'resource_id': '....',
      'filters': {
        'occurrenceID': '...'
      },
      'errors': ['ZERO_COORDINATE', 'DEPTH_NOT_METRIC'],
      'force': True
    })
```

Externally:
```
curl http://.../api/3/action/update_record_dqi -H "Authorization: ..." -d '{"resource_id": "...", "filters": {"_id": 3}, "errors": ["TAXON_MATCH_NONE"], "force": true}'
```