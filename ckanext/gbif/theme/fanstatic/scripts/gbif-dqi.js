/*
 * Load data errors from gbif
 */
this.ckan.module('gbif-dqi', function ($, _) {
    var self;

    return {

        options: {
            gbifId: '',
            gbifErrors: {}
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
                issue = this.options.gbifErrors[data['issues'][i]]
                $ul.append("<li class='"+ issue['severity'].toLowerCase().replace(/[^a-z]/g, '-') +"'><abbr title='" + issue['description'] + "'>" + issue['title'] + "</abbr></li>");
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