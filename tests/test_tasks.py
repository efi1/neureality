import pytest
import requests
from tests.cfg.cfg_global import settings
from importlib.resources import files
from conftest import cfg_get_data, logger


@pytest.mark.parametrize('test_name', [resource.name for resource in files(settings.cfg_tests_dir).iterdir()])
def test_perform_tasks(app_container: object, test_name: str) -> None:
    """
    Testing various task using the files in app.cfg.cfg_tests as input (parameterized test)
    :param app_container: the docker container in which the app resides in
    :param test_name: test name as taken from tests.cfg.cfg_tests folder
    :return: no return. assertion is made on the api response
    """
    cfg_data = cfg_get_data(test_name) # test data
    task_data = cfg_data.task_data # request data
    req_type = task_data.request_type # GET or POST request
    expected_data = cfg_data.return_data # expected response of the request
    api_path = cfg_data.api_path
    uri = f'{settings.base_url}{api_path}'
    log_msg = f'calling get {uri}' if req_type == 'get' else f'calling post {uri}, data: {task_data.model_dump()}'
    logger.info(F"api-client request: {log_msg}")
    # execute the api call
    response = requests.get(uri) if req_type == 'get' else requests.post(uri, json=task_data.model_dump())
    res = response.json()
    logger.info(F"response from api-client: {res}")
    # Check that the API response is as expected
    assert response.status_code == expected_data.status_code, \
        F"Expected status code: {expected_data.status_code}, actual: {response.status_code}"
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res.get('result') == expected_data.return_value, (F"wrong response val: {res['return_value']}, "
                                                                 F"expected: {expected_data.return_value}")

