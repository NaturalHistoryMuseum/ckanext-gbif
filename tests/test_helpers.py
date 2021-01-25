from ckanext.gbif.lib.helpers import dqi_parse_errors, dqi_get_severity

from ckanext.gbif.lib.errors import GBIF_ERRORS, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS
from mock import MagicMock


class TestDQIParseErrors(object):

    def test_empty(self):
        assert dqi_parse_errors([]) == []

    def test_one_match(self):
        name = u'BASIS_OF_RECORD_INVALID'
        assert dqi_parse_errors([name]) == [GBIF_ERRORS[name]]

    def test_all_match(self):
        names = list(GBIF_ERRORS.keys())
        assert dqi_parse_errors(names) == list(GBIF_ERRORS.values())

    def test_unmapped(self):
        # this is important because we want to avoid erroring if GBIF add new errors which we
        # haven't added to the extension yet
        name = u'SOME_NON_GBIF_CODE'
        assert dqi_parse_errors([name]) == []

    def test_mixed(self):
        valid = u'COORDINATE_REPROJECTION_FAILED'
        invalid = u'SOME_NON_GBIF_CODE'
        assert dqi_parse_errors([valid, invalid]) == [GBIF_ERRORS[valid]]


class TestDQIGetSeverity(object):

    def test_no_gbif_id(self):
        assert dqi_get_severity(MagicMock(), None) == u'unknown'

    def test_no_errors(self):
        assert dqi_get_severity([], MagicMock()) == u'No errors'

    def test_only_major(self):
        errors = [
            {
                u'severity': DQI_MAJOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == u'Major errors'

    def test_only_minor(self):
        errors = [
            {
                u'severity': DQI_MINOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == u'Minor errors'

    def test_mixed_levels(self):
        errors = [
            {
                u'severity': DQI_MINOR_ERRORS
            },
            {
                u'severity': DQI_MINOR_ERRORS
            },
            {
                u'severity': DQI_MAJOR_ERRORS
            },
            {
                u'severity': DQI_MINOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == u'Major errors'
