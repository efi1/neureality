import logging
import pytest
from tests.cfg.cfg_global import settings
from importlib.resources import files
from conftest import cfg_get_data
from app.clients.fastapi.tasks_base import app


@pytest.mark.parametrize('test_name', [resource.name for resource in files(settings.cfg_tests_dir).iterdir()])
def test_perform_tasks(api_client: app, test_name: str) -> None:
    """
    Testing various task using the files in app.cfg.cfg_tests as input (parameterized test)
    :param api_client: the FastAPI client
    :param test_name: test name as taken from app.cfg.cfg_tests folder
    :return:
    """
    cfg_data = cfg_get_data(test_name)
    task_data = cfg_data['task_data']
    req_type = task_data['request_type']
    expected_data = cfg_data['return_data']
    api_path = cfg_data['api_path']
    response = api_client.get(api_path) if req_type == 'get' else api_client.post(api_path, json=task_data)
    res = response.json()
    logging.info(F"response from api-client: {res}")
    assert response.status_code == expected_data['status_code'], \
        F"Expected status code: {expected_data['status_code']}, actual: {response.status_code}"
    if expected_data['validate_resp_val']:
        assert res.get('result') == expected_data[
            'return_value'], F"wrong response val: {res['return_value']}, expected: {expected_data['return_value']}"



