import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from checkin import get_user_info


def test_get_user_info_handles_invalid_json_response():
	client = MagicMock()
	response = MagicMock()
	response.status_code = 200
	response.headers = {'content-type': 'text/html'}
	response.text = '<html>blocked</html>'
	response.json.side_effect = json.JSONDecodeError('Expecting value', '', 0)
	client.get.return_value = response

	result = get_user_info(client, {}, 'https://example.com/api/user/self')

	assert result['success'] is False
	assert 'Invalid JSON response' in result['error']
	assert 'content-type=text/html' in result['error']
	assert 'body=<html>blocked</html>' in result['error']


def test_get_user_info_returns_parsed_balance_for_valid_payload():
	client = MagicMock()
	response = MagicMock()
	response.status_code = 200
	response.json.return_value = {
		'success': True,
		'data': {'quota': 2500000, 'used_quota': 500000},
	}
	client.get.return_value = response

	result = get_user_info(client, {}, 'https://example.com/api/user/self')

	assert result == {
		'success': True,
		'quota': 5.0,
		'used_quota': 1.0,
		'display': ':money: Current balance: $5.0, Used: $1.0',
	}
