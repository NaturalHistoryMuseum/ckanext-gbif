#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import ckan.model as model
from ckan.model.resource import Resource
from sqlalchemy import MetaData, Column, Integer, String, DateTime, UnicodeText, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GBIFDownloadStats(Base):
    """
    Table for holding resource stats
    """
    __tablename__ = 'gbif_download_stats'
    doi = Column(UnicodeText, primary_key=True)
    date = Column(DateTime)  # Date of download
    count = Column(Integer)
