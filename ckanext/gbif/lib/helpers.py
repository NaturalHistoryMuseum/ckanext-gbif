
import logging
import json
import urllib
import re
import os
import urllib

from beaker.cache import cache_region
from pylons import config
from collections import OrderedDict
from jinja2.filters import do_truncate

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import c, _, request
from ckan.lib.helpers import url_for, link_to, snippet, _follow_objects, _VALID_GRAVATAR_DEFAULTS, get_allowed_view_types as ckan_get_allowed_view_types
from webhelpers.html import literal

from ckanext.nhm.lib.form import list_to_form_options
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY, UPDATE_FREQUENCIES
from ckanext.nhm.views import *
from ckanext.nhm.lib.resource import (
    resource_get_ordered_fields,
    resource_filter_options,
    parse_request_filters,
    FIELD_DISPLAY_FILTER,
    resource_filter_get_cookie,
    resource_filter_set_cookie,
    resource_filter_delete_cookie
)

log = logging.getLogger(__name__)


def dqi_get_status_pill(dqi_status):
    """
    Convert a DQI status string into a class name
    @param dqi_status: Minor errors etc.,
    @return: minor-errors
    """

    cls = 'dqi-{0}'.format(dqi_status.lower().replace(' ', '-'))

    return literal(
        '''
        <span title="{0}" class="dqi-pill {1}">{0}</span>
        '''.format(dqi_status, cls))

