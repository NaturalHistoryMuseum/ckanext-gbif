from unittest.mock import MagicMock

from ckanext.gbif.lib.errors import GBIF_ERRORS, DQI_MAJOR_ERRORS, DQI_MINOR_ERRORS
from ckanext.gbif.lib.helpers import dqi_parse_errors, dqi_get_severity


class TestDQIParseErrors:

    def test_empty(self):
        assert dqi_parse_errors([]) == []

    def test_one_match(self):
        name = 'BASIS_OF_RECORD_INVALID'
        assert dqi_parse_errors([name]) == [GBIF_ERRORS[name]]

    def test_all_match(self):
        names = list(GBIF_ERRORS.keys())
        assert dqi_parse_errors(names) == list(GBIF_ERRORS.values())

    def test_unmapped(self):
        # this is important because we want to avoid erroring if GBIF add new errors which we
        # haven't added to the extension yet
        name = 'SOME_NON_GBIF_CODE'
        assert dqi_parse_errors([name]) == []

    def test_mixed(self):
        valid = 'COORDINATE_REPROJECTION_FAILED'
        invalid = 'SOME_NON_GBIF_CODE'
        assert dqi_parse_errors([valid, invalid]) == [GBIF_ERRORS[valid]]


class TestDQIGetSeverity:

    def test_no_gbif_id(self):
        assert dqi_get_severity(MagicMock(), None) == 'unknown'

    def test_no_errors(self):
        assert dqi_get_severity([], MagicMock()) == 'No errors'

    def test_only_major(self):
        errors = [
            {
                'severity': DQI_MAJOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == 'Major errors'

    def test_only_minor(self):
        errors = [
            {
                'severity': DQI_MINOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == 'Minor errors'

    def test_mixed_levels(self):
        errors = [
            {
                'severity': DQI_MINOR_ERRORS
            },
            {
                'severity': DQI_MINOR_ERRORS
            },
            {
                'severity': DQI_MAJOR_ERRORS
            },
            {
                'severity': DQI_MINOR_ERRORS
            }
        ]
        assert dqi_get_severity(errors, MagicMock()) == 'Major errors'
