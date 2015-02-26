/*
 * Load data errors from gbif
 */
this.ckan.module('gbif-dqi', function ($, _) {
    var self;

    var GBIFErrors = {
        'BASIS_OF_RECORD_INVALID': {'title': 'Basis of record invalid', 'description': 'The given basis of record is impossible to interpret or seriously different from the recommended vocabulary.'},
        'CONTINENT_COUNTRY_MISMATCH': {'title': 'Continent country mismatch', 'description': 'The interpreted continent and country do not match up.'},
        'CONTINENT_DERIVED_FROM_COORDINATES': {'title': 'Continent derived from coordinates', 'description': 'The interpreted continent is based on the coordinates, not the verbatim string information.'},
        'CONTINENT_INVALID': {'title': 'Continent invalid', 'description': 'Uninterpretable continent values found.'},
        'COORDINATE_INVALID': {'title': 'Coordinate invalid', 'description': 'Coordinate value given in some form but GBIF is unable to interpret it.'},
        'COORDINATE_OUT_OF_RANGE': {'title': 'Coordinate out of range', 'description': 'Coordinate has invalid lat/lon values out of their decimal max range.'},
        'COORDINATE_REPROJECTED': {'title': 'Coordinate reprojected', 'description': 'The original coordinate was successfully reprojected from a different geodetic datum to WGS84.'},
        'COORDINATE_REPROJECTION_FAILED': {'title': 'Coordinate reprojection failed', 'description': 'The given decimal latitude and longitude could not be reprojected to WGS84 based on the provided datum.'},
        'COORDINATE_REPROJECTION_SUSPICIOUS': {'title': 'Coordinate reprojection suspicious', 'description': 'Indicates successful coordinate reprojection according to provided datum, but which results in a datum shift larger than 0.1 decimal degrees.'},
        'COORDINATE_ROUNDED': {'title': 'Coordinate rounded', 'description': 'Original coordinate modified by rounding to 5 decimals.'},
        'COUNTRY_COORDINATE_MISMATCH': {'title': 'Country coordinate mismatch', 'description': 'The interpreted occurrence coordinates fall outside of the indicated country.'},
        'COUNTRY_DERIVED_FROM_COORDINATES': {'title': 'Country derived from coordinates', 'description': 'The interpreted country is based on the coordinates, not the verbatim string information.'},
        'COUNTRY_INVALID': {'title': 'Country invalid', 'description': 'Uninterpretable country values found.'},
        'COUNTRY_MISMATCH': {'title': 'Country mismatch', 'description': 'Interpreted country for dwc:country and dwc:countryCode contradict each other.'},
        'DEPTH_MIN_MAX_SWAPPED': {'title': 'Depth min max swapped', 'description': 'Set if supplied min>max'},
        'DEPTH_NON_NUMERIC': {'title': 'Depth non numeric', 'description': 'Set if depth is a non numeric value'},
        'DEPTH_NOT_METRIC': {'title': 'Depth not metric', 'description': 'Set if supplied depth is not given in the metric system, for example using feet instead of meters'},
        'DEPTH_UNLIKELY': {'title': 'Depth unlikely', 'description': 'Set if depth is larger than 11.000m or negative.'},
        'ELEVATION_MIN_MAX_SWAPPED': {'title': 'Elevation min max swapped', 'description': 'Set if supplied min > max elevation'},
        'ELEVATION_NON_NUMERIC': {'title': 'Elevation non numeric', 'description': 'Set if elevation is a non numeric value'},
        'ELEVATION_NOT_METRIC': {'title': 'Elevation not metric', 'description': 'Set if supplied elevation is not given in the metric system, for example using feet instead of meters'},
        'ELEVATION_UNLIKELY': {'title': 'Elevation unlikely', 'description': 'Set if elevation is above the troposphere (17km) or below 11km (Mariana Trench).'},
        'GEODETIC_DATUM_ASSUMED_WGS84': {'title': 'Geodetic datum assumed WGS84', 'description': 'Indicating that the interpreted coordinates assume they are based on WGS84 datum as the datum was either not indicated or interpretable.'},
        'GEODETIC_DATUM_INVALID': {'title': 'Geodetic datum invalid', 'description': 'The geodetic datum given could not be interpreted.'},
        'IDENTIFIED_DATE_INVALID': {'title': 'Identified date invalid', 'description': 'The date given for dwc:dateIdentified is invalid and cant be interpreted at all.'},
        'IDENTIFIED_DATE_UNLIKELY': {'title': 'Identified date unlikely', 'description': 'The date given for dwc:dateIdentified is in the future or before Linnean times (1700).'},
        'MODIFIED_DATE_INVALID': {'title': 'Modified date invalid', 'description': 'A (partial) invalid date is given for dc:modified, such as a non existing date, invalid zero month, etc.'},
        'MODIFIED_DATE_UNLIKELY': {'title': 'Modified date unlikely', 'description': 'The date given for dc:modified is in the future or predates unix time (1970).'},
        'MULTIMEDIA_DATE_INVALID': {'title': 'Multimedia date invalid', 'description': 'An invalid date is given for dc:created of a multimedia object.'},
        'MULTIMEDIA_URI_INVALID': {'title': 'Multimedia uri invalid', 'description': 'An invalid uri is given for a multimedia object.'},
        'PRESUMED_NEGATED_LATITUDE': {'title': 'Presumed negated latitude', 'description': 'Latitude appears to be negated, e.g.'},
        'PRESUMED_NEGATED_LONGITUDE': {'title': 'Presumed negated longitude', 'description': 'Longitude appears to be negated, e.g.'},
        'PRESUMED_SWAPPED_COORDINATE': {'title': 'Presumed swapped coordinate', 'description': 'Latitude and longitude appear to be swapped.'},
        'RECORDED_DATE_INVALID': {'title': 'Recorded date invalid', 'description': 'A (partial) invalid date is given, such as a non existing date, invalid zero month, etc.'},
        'RECORDED_DATE_MISMATCH': {'title': 'Recorded date mismatch', 'description': 'The recording date specified as the eventDate string and the individual year, month, day are contradicting.'},
        'RECORDED_DATE_UNLIKELY': {'title': 'Recorded date unlikely', 'description': 'The recording date is highly unlikely, falling either into the future or represents a very old date before 1600 that predates modern taxonomy.'},
        'REFERENCES_URI_INVALID': {'title': 'References uri invalid', 'description': 'An invalid uri is given for dc:references.'},
        'TAXON_MATCH_FUZZY': {'title': 'Taxon match fuzzy', 'description': 'Matching to the taxonomic backbone can only be done using a fuzzy, non exact match.'},
        'TAXON_MATCH_HIGHERRANK': {'title': 'Taxon match higherrank', 'description': 'Matching to the taxonomic backbone can only be done on a higher rank and not the scientific name.'},
        'TAXON_MATCH_NONE': {'title': 'Taxon match none', 'description': 'Matching to the taxonomic backbone cannot be done cause there was no match at all or several matches with too little information to keep them apart (homonyms).'},
        'TYPE_STATUS_INVALID': {'title': 'Type status invalid', 'description': 'The given type status is impossible to interpret or seriously different from the recommended vocabulary.'},
        'ZERO_COORDINATE': {'title': 'Zero coordinate', 'description': 'Coordinate is the exact 0/0 coordinate, often indicating a bad null coordinate.'}
    }

    return {

        options: {
            gbifId: ''
        },

        /* Initialises the module setting up elements and event listeners.
         *
         * Returns nothing.
         */
        initialize: function () {

            this.$pill = this.$('span.dqi-major-errors, span.dqi-minor-errors');
            this.$errors = this.$('div.dqi-errors')
            this.$pill.on('click', jQuery.proxy(this._onClick, this));

            // If anyone clicks anywhere else on the page, hide it
            $('body').on('click', jQuery.proxy(this.hide, this))
            $('div.dqi-errors').on('click', function(e){e.stopPropagation();})

        },

        _onClick: function (e) {

            // Is this active?
            if (this.el.hasClass('active')) {
                this.hide()
            } else {
                this.show()
            }

            e.preventDefault();
            return false;
        },

        _ajaxError: function () {
            this.$errors.html('<p>Sorry, we could not retrieve quality indicators.</p>');
        },

        _ajaxSuccess: function (data) {
            $ul = $("<ul>");
            for (var i = 0; i < data['issues'].length; i++) {
                issue = GBIFErrors[data['issues'][i]]
                $ul.append("<li><abbr title='" + issue['description'] + "'>" + issue['title'] + "</abbr></li>");
            }
            this.$errors.html($ul);
        },

        hide: function () {
            this.el.removeClass('active');
        },

        show: function () {

            // Mark the module element as active
            this.el.addClass('active');

            // If this has already run (contains the UL)
            if (!$.contains(this.el, 'ul')) {
                $.ajax({
                    url: 'http://api.gbif.org/v1/occurrence/' + this.options.gbifId,
                    type: 'GET',
                    error: jQuery.proxy(this._ajaxError, this),
                    success: jQuery.proxy(this._ajaxSuccess, this),
                    timeout: 300
                })
            }

        }


    }
});