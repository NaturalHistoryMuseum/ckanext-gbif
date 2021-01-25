import pytest
from ckan.plugins import toolkit
from mock import patch, MagicMock, call

from ckanext.gbif.logic.action import gbif_record_show


@patch(u'ckanext.gbif.logic.action.requests')
class TestGBIFRecordShow(object):

    def test_success(self, requests_mock):
        gbif_id = u'test'
        mock_response = MagicMock(status_code=200)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        record = gbif_record_show(MagicMock(), dict(gbif_id=gbif_id))
        assert record == mock_response.json()
        assert requests_mock.get.call_args == call(u'https://api.gbif.org/v1/occurrence/test')

    def test_failure(self, requests_mock):
        gbif_id = u'test'
        mock_response = MagicMock(status_code=404)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        with pytest.raises(toolkit.ObjectNotFound):
            gbif_record_show(MagicMock(), dict(gbif_id=gbif_id))
        assert requests_mock.get.call_args == call(u'https://api.gbif.org/v1/occurrence/test')

    def test_missing_gbif_id(self, requests_mock):
        with pytest.raises(toolkit.ValidationError):
            gbif_record_show(MagicMock(), {})

    @pytest.mark.ckan_config(u'ckan.plugins', u'gbif')
    @pytest.mark.usefixtures(u'with_plugins')
    def test_action_through_ckan(self, requests_mock):
        '''
        Just to make sure the plugin is all wired up right run the success test through the
        get_action toolkit function instead of calling the gbif_record_show function directly.
        '''
        gbif_id = u'test'
        mock_response = MagicMock(status_code=200)
        requests_mock.configure_mock(get=MagicMock(return_value=mock_response))
        record = toolkit.get_action(u'gbif_record_show')({}, dict(gbif_id=gbif_id))
        assert record == mock_response.json()
        assert requests_mock.get.call_args == call(u'https://api.gbif.org/v1/occurrence/test')
