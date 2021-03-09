from unittest.mock import patch, MagicMock, call

import pytest
from ckan.plugins import toolkit

from ckanext.gbif.logic.action import gbif_record_show


@patch('ckanext.gbif.logic.action.requests')
class TestGBIFRecordShow:

    def test_success(self, requests_mock):
        gbif_id = 'test'
        mock_response = MagicMock(status_code=200)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        record = gbif_record_show(MagicMock(), dict(gbif_id=gbif_id))
        assert record == mock_response.json()
        assert requests_mock.get.call_args == call(f'https://api.gbif.org/v1/occurrence/{gbif_id}')

    def test_failure(self, requests_mock):
        gbif_id = 'test'
        mock_response = MagicMock(status_code=404)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        with pytest.raises(toolkit.ObjectNotFound):
            gbif_record_show(MagicMock(), dict(gbif_id=gbif_id))
        assert requests_mock.get.call_args == call(f'https://api.gbif.org/v1/occurrence/{gbif_id}')

    def test_missing_gbif_id(self, requests_mock):
        with pytest.raises(toolkit.ValidationError):
            gbif_record_show(MagicMock(), {})

    @pytest.mark.ckan_config('ckan.plugins', 'gbif')
    @pytest.mark.usefixtures('with_plugins')
    def test_action_through_ckan(self, requests_mock):
        '''
        Just to make sure the plugin is all wired up right run the success test through the
        get_action toolkit function instead of calling the gbif_record_show function directly.
        '''
        gbif_id = 'test'
        mock_response = MagicMock(status_code=200)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        record = toolkit.get_action('gbif_record_show')({}, dict(gbif_id=gbif_id))
        assert record == mock_response.json()
        assert requests_mock.get.call_args == call(f'https://api.gbif.org/v1/occurrence/{gbif_id}')
