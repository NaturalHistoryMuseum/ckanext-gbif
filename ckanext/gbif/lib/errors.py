#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gbif
# Created by the Natural History Museum in London, UK


DQI_MAJOR_ERRORS = u'Major errors'
DQI_MINOR_ERRORS = u'Minor errors'

GBIF_ERRORS = {
    u'BASIS_OF_RECORD_INVALID': {
        u'severity': DQI_MAJOR_ERRORS,
        u'title': u'Basis of record invalid',
        u'description': u'The given basis of record is impossible to interpret or '
                        u'seriously different from the recommended vocabulary.'
        },
    u'CONTINENT_COUNTRY_MISMATCH': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Continent country mismatch',
        u'description': u'The interpreted continent and country do not match up.'
        },
    u'CONTINENT_DERIVED_FROM_COORDINATES': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Continent derived from coordinates',
        u'description': u'The interpreted continent is based on the coordinates, '
                        u'not the verbatim string information.'
        },
    u'CONTINENT_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Continent invalid',
        u'description': u'Uninterpretable continent values found.'
        },
    u'COORDINATE_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate invalid',
        u'description': u'Coordinate value given in some form but GBIF is unable to '
                        u'interpret it.'
        },
    u'COORDINATE_OUT_OF_RANGE': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate out of range',
        u'description': u'Coordinate has invalid lat/lon values out of their decimal '
                        u'max range.'
        },
    u'COORDINATE_REPROJECTED': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate reprojected',
        u'description': u'The original coordinate was successfully reprojected from a '
                        u'different geodetic datum to WGS84.'
        },
    u'COORDINATE_REPROJECTION_FAILED': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate reprojection failed',
        u'description': u'The given decimal latitude and longitude could not be '
                        u'reprojected to WGS84 based on the provided datum.'
        },
    u'COORDINATE_REPROJECTION_SUSPICIOUS': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate reprojection suspicious',
        u'description': u'Indicates successful coordinate reprojection according to '
                        u'provided datum, but which results in a datum shift larger '
                        u'than 0.1 decimal degrees.'
        },
    u'COORDINATE_ROUNDED': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Coordinate rounded',
        u'description': u'Original coordinate modified by rounding to 5 decimals.'
        },
    u'COUNTRY_COORDINATE_MISMATCH': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Country coordinate mismatch',
        u'description': u'The interpreted occurrence coordinates fall outside of the '
                        u'indicated country.'
        },
    u'COUNTRY_DERIVED_FROM_COORDINATES': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Country derived from coordinates',
        u'description': u'The interpreted country is based on the coordinates, '
                        u'not the verbatim string information.'
        },
    u'COUNTRY_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Country invalid',
        u'description': u'Uninterpretable country values found.'
        },
    u'COUNTRY_MISMATCH': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Country mismatch',
        u'description': u'Interpreted country for dwc:country and dwc:countryCode '
                        u'contradict each other.'
        },
    u'DEPTH_MIN_MAX_SWAPPED': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Depth min max swapped',
        u'description': u'Set if supplied min>max'
        },
    u'DEPTH_NON_NUMERIC': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Depth non numeric',
        u'description': u'Set if depth is a non numeric value'
        },
    u'DEPTH_NOT_METRIC': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Depth not metric',
        u'description': u'Set if supplied depth is not given in the metric system, '
                        u'for example using feet instead of meters'
        },
    u'DEPTH_UNLIKELY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Depth unlikely',
        u'description': u'Set if depth is larger than 11.000m or negative.'
        },
    u'ELEVATION_MIN_MAX_SWAPPED': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Elevation min max swapped',
        u'description': u'Set if supplied min > max elevation'
        },
    u'ELEVATION_NON_NUMERIC': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Elevation non numeric',
        u'description': u'Set if elevation is a non numeric value'
        },
    u'ELEVATION_NOT_METRIC': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Elevation not metric',
        u'description': u'Set if supplied elevation is not given in the metric system, '
                        u'for example using feet instead of meters'
        },
    u'ELEVATION_UNLIKELY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Elevation unlikely',
        u'description': u'Set if elevation is above the troposphere (17km) or below '
                        u'11km (Mariana Trench).'
        },
    u'GEODETIC_DATUM_ASSUMED_WGS84': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Geodetic datum assumed WGS84',
        u'description': u'Indicating that the interpreted coordinates assume they are '
                        u'based on WGS84 datum as the datum was either not indicated '
                        u'or interpretable.'
        },
    u'GEODETIC_DATUM_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Geodetic datum invalid',
        u'description': u'The geodetic datum given could not be interpreted.'
        },
    u'IDENTIFIED_DATE_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Identified date invalid',
        u'description': u'The date given for dwc:dateIdentified is invalid and cant be '
                        u'interpreted at all.'
        },
    u'IDENTIFIED_DATE_UNLIKELY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Identified date unlikely',
        u'description': u'The date given for dwc:dateIdentified is in the future or '
                        u'before Linnean times (1700).'
        },
    u'MODIFIED_DATE_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Modified date invalid',
        u'description': u'A (partial) invalid date is given for dc:modified, such as a '
                        u'non existing date, invalid zero month, etc.'
        },
    u'MODIFIED_DATE_UNLIKELY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Modified date unlikely',
        u'description': u'The date given for dc:modified is in the future or predates '
                        u'unix time (1970).'
        },
    u'MULTIMEDIA_DATE_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Multimedia date invalid',
        u'description': u'An invalid date is given for dc:created of a multimedia '
                        u'object.'
        },
    u'MULTIMEDIA_URI_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Multimedia uri invalid',
        u'description': u'An invalid uri is given for a multimedia object.'
        },
    u'PRESUMED_NEGATED_LATITUDE': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Presumed negated latitude',
        u'description': u'Latitude appears to be negated, e.g.'
        },
    u'PRESUMED_NEGATED_LONGITUDE': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Presumed negated longitude',
        u'description': u'Longitude appears to be negated, e.g.'
        },
    u'PRESUMED_SWAPPED_COORDINATE': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Presumed swapped coordinate',
        u'description': u'Latitude and longitude appear to be swapped.'
        },
    u'RECORDED_DATE_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Recorded date invalid',
        u'description': u'A (partial) invalid date is given, such as a non existing '
                        u'date, invalid zero month, etc.'
        },
    u'RECORDED_DATE_MISMATCH': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Recorded date mismatch',
        u'description': u'The recording date specified as the eventDate string and the '
                        u'individual year, month, day are contradicting.'
        },
    u'RECORDED_DATE_UNLIKELY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Recorded date unlikely',
        u'description': u'The recording date is highly unlikely, falling either into '
                        u'the future or represents a very old date before 1600 that '
                        u'predates modern taxonomy.'
        },
    u'REFERENCES_URI_INVALID': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'References uri invalid',
        u'description': u'An invalid uri is given for dc:references.'
        },
    u'TAXON_MATCH_FUZZY': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Taxon match fuzzy',
        u'description': u'Matching to the taxonomic backbone can only be done using a '
                        u'fuzzy, non exact match.'
        },
    u'TAXON_MATCH_HIGHERRANK': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Taxon match higherrank',
        u'description': u'Matching to the taxonomic backbone can only be done on a '
                        u'higher rank and not the scientific name.'
        },
    u'TAXON_MATCH_NONE': {
        u'severity': DQI_MAJOR_ERRORS,
        u'title': u'Taxon match none',
        u'description': u'Matching to the taxonomic backbone cannot be done cause '
                        u'there was no match at all or several matches with too little '
                        u'information to keep them apart (homonyms).'
        },
    u'TYPE_STATUS_INVALID': {
        u'severity': DQI_MAJOR_ERRORS,
        u'title': u'Type status invalid',
        u'description': u'The given type status is impossible to interpret or '
                        u'seriously different from the recommended vocabulary.'
        },
    u'ZERO_COORDINATE': {
        u'severity': DQI_MINOR_ERRORS,
        u'title': u'Zero coordinate',
        u'description': u'Coordinate is the exact 0/0 coordinate, often indicating a '
                        u'bad null coordinate.'
        }
    }
