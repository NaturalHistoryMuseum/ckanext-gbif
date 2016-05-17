# ckanext-gbif

This module loads the GBIF dataset back into the portal. 


USAGE
=====

The GBIF dataset download is received via email, so the GBIF download needs to be manually uploaded to the server.

1. Go to http://www.gbif.org/occurrence/search?datasetKey=7e380070-f762-11e1-a439-00145eb45e9a#
2. Request download of all occurrence records
3. When the email received, upload the archive file to the import directory (setting ckanext.gbif.import_dir)  
 

Run paster gbif load-dataset -c [path to config]
 
 
CRON
==== 

The command is run weekly as a cron job.

paster gbif load-dataset -c [path to config]


If a recent GBIF dataset download cannot be found in the import directory (setting ckanext.gbif.import_dir), a warning email will be sent to pylons.config.get('email_to') (currently data@data.nhm.ac.uk). 



Dependencies
============

This module depends on ckanext-nhm


Settings
========

ckanext.gbif.dataset_key - The UUID of the NHM occurrence dataset on GBIF (http://www.gbif.org/dataset/7e380070-f762-11e1-a439-00145eb45e9a) 
ckanext.gbif.organisation_key - The UUID of the NHM organisation on GBIF (http://www.gbif.org/publisher/19456090-b49a-11d8-abeb-b8a03c50a862)
ckanext.gbif.import_dir - Directory holding the GBIF archive files


TODO
====

Automate requesting and loading of GBIF dataset to the server. 