from unittest.mock import MagicMock, patch

import pytest

from agno.tools.directus import DirectusTools


@pytest.fixture
def directus_tools():
    return DirectusTools(url="http://localhost:8055", api_token="test-token")


def test_get_headers(directus_tools):
    headers = directus_tools._get_headers()
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"


@patch("httpx.Client")
def test_list_experiments(mock_client, directus_tools):
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": "1", "hypothesis": "test"}]}
    mock_client.return_value.__enter__.return_value.request.return_value = mock_response

    result = directus_tools.list_experiments()
    assert "test" in result
    mock_client.return_value.__enter__.return_value.request.assert_called_once()
    args, kwargs = mock_client.return_value.__enter__.return_value.request.call_args
    assert kwargs["method"] == "GET"
    assert "experiments" in kwargs["url"]


@patch("httpx.Client")
def test_create_experiment(mock_client, directus_tools):
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"id": "new-id", "hypothesis": "new-hyp"}}
    mock_client.return_value.__enter__.return_value.request.return_value = mock_response

    result = directus_tools.create_experiment(hypothesis="new-hyp", impact=8, confidence=7, ease=6)
    assert "new-id" in result
    mock_client.return_value.__enter__.return_value.request.assert_called_once()
    args, kwargs = mock_client.return_value.__enter__.return_value.request.call_args
    assert kwargs["method"] == "POST"
    assert kwargs["json"]["hypothesis"] == "new-hyp"


@patch("httpx.Client")
def test_create_task(mock_client, directus_tools):
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"id": "task-id", "description": "task-desc"}}
    mock_client.return_value.__enter__.return_value.request.return_value = mock_response

    result = directus_tools.create_task(description="task-desc", experiment_id="exp-id")
    assert "task-id" in result
    mock_client.return_value.__enter__.return_value.request.assert_called_once()
    args, kwargs = mock_client.return_value.__enter__.return_value.request.call_args
    assert kwargs["method"] == "POST"
    assert kwargs["json"]["experiment_id"] == "exp-id"
