<!--header-start-->
<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-gbif

[![Tests](https://img.shields.io/github/workflow/status/NaturalHistoryMuseum/ckanext-gbif/Tests?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-gbif/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-gbif/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-gbif)
[![CKAN](https://img.shields.io/badge/ckan-2.9.1-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-gbif?style=flat-square)](https://ckanext-gbif.readthedocs.io)

_A CKAN extension that that connects with the GBIF API._

<!--header-end-->

# Overview

<!--overview-start-->
This extension retrieves additional data (e.g. DQIs) from the [GBIF](https://gbif.org) API for a record with an associated GBIF ID.

This extension also provides some templates for displaying these data.

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-gbif.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-gbif
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-gbif
  python setup.py develop
  ```

5. Add 'gbif' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... gbif
  ```

<!--installation-end-->

# Configuration

<!--configuration-start-->
These are the options that can be specified in your .ini config file.

## Template variables **[REQUIRED]**

Name|Description
----|-----------
`ckanext.gbif.organisation_key`|For linking to the dataset publisher (i.e. https://gbif.org/publisher/ORG_KEY)
`ckanext.gbif.dataset_key`|For linking to the dataset itself (i.e. https://gbif.org/dataset/DATA_KEY)

<!--configuration-end-->

# Usage

<!--usage-start-->
## Actions

### `gbif_record_show`
Get the associated GBIF data for a record.

```python
from ckan.plugins import toolkit

gbif_record = toolkit.get_action(u'gbif_record_show')(context, {
    u'occurrence_id': record_gbif_occurrence_id
    })
```

## Templates

The templates inherit from `record/specimen.html` and `record/dwc.html` and will insert a link to the GBIF view in the `content_primary_nav` block.

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images
```bash
docker-compose build
```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
```bash
docker-compose run ckan
```

The ckan image uses the Dockerfile in the `docker/` folder.

<!--testing-end-->
