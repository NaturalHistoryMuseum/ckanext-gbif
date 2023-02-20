/*
 * Load data errors from gbif
 */
this.ckan.module('gbif-dqi', function ($, _) {
  var self;

  return {
    options: {
      gbifId: '',
    },

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      // Only add interactions if we have gbifId
      if (this.options.gbifId) {
        this.$pill = this.$('span.dqi-major-errors, span.dqi-minor-errors');
        this.$pill.on('click', jQuery.proxy(this._onClick, this));
        // If anyone clicks anywhere else on the page, hide it
        $('body').on('click', jQuery.proxy(this.hide, this));
        $('div.dqi-errors').on('click', function (e) {
          e.stopPropagation();
        });
      }
    },

    _onClick: function (e) {
      // Is this active?
      if (this.el.hasClass('active')) {
        this.hide();
      } else {
        this.show();
      }

      e.preventDefault();
      return false;
    },

    hide: function () {
      this.el.removeClass('active');
    },

    show: function () {
      // Mark the module element as active
      this.el.addClass('active');
    },
  };
});
