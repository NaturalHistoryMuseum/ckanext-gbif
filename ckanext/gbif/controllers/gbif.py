
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class GBIFController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def record(self):
        return p.toolkit.render('about/citation.html', {'title': 'Citation and attribution'})

