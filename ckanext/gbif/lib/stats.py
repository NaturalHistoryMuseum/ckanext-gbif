#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '01/08/2017'.
"""

import os
import re
import pylons
import requests
import datetime
from bs4 import BeautifulSoup

import ckan.model as model
from ckanext.gbif.model.stats import Base, GBIFDownloadStats

OFFSET_INTERVAL = 10  # Num per page, on GBIF known as offset interval


def gbif_download_parse_stats():
    """
    Scrape the GBIF site for download events of Museum records
    Cache the results for 4 hours so rerunning with different params doesn't take ages
    :return:
    """

    gbif_dataset_uuid = pylons.config['ckanext.gbif.dataset_key']

    offset = 0

    Base.metadata.create_all(model.meta.engine)

    while True:
        print 'Retrieving page offset %s' % offset

        # Build URL
        url = os.path.join('http://www.gbif.org/dataset', gbif_dataset_uuid, 'activity')
        r = requests.get(url, params={'offset': offset})
        # Get some soup
        soup = BeautifulSoup(r.content, "html.parser")

        records = soup.find_all('div', class_="result")

        if not records:
            break

        for record in records:
            download_dt = record.find("dt", text="Download")
            download_dd = download_dt.find_next('dd')

            date_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', download_dd.contents[2].strip())
            date_object = datetime.datetime.strptime(date_str, '%d %B %Y')

            # Get the DOI from the download info
            doi_link = download_dd.find('a', href=True)
            doi = re.search(r'/([0-9\-]+)$', doi_link['href']).group(1)

            # Lets get the counts
            records_dt = record.find("dt", text="Records")
            count = re.search(r'(\d+)', records_dt.find_next('dd').text).group(1)

            # If we have this DOI already, then we have reached the end of
            # the stats that need processing
            if model.Session.query(GBIFDownloadStats).get(doi):
                model.Session.commit()
                return

            model.Session.add(GBIFDownloadStats(doi=doi, date=date_object, count=count))

        # Increment offset by interval
        offset += OFFSET_INTERVAL

        model.Session.commit()

