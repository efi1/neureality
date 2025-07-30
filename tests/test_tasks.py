from typing import Tuple
import pytest
import requests
from requests import Response
from tests.cfg.cfg_global import settings
from importlib.resources import files
from conftest import get_param_data, logger
from tests.utils.data_to_obj import FullRequest, ReturnData


def shared_test_logic(cfg_data: FullRequest) -> Tuple[Response, ReturnData]:
    task_data = cfg_data.task_data # request data
    req_type = task_data.request_type # GET or POST request
    expected_data = cfg_data.return_data # expected response of the request
    api_path = cfg_data.api_path
    uri = f'{settings.base_url}{api_path}'
    log_msg = f'calling get {uri}' if req_type == 'get' else f'calling post {uri}, data: {task_data.model_dump()}'
    logger.info(F"api-client request: {log_msg}")
    # execute the api call
    response = requests.get(uri) if req_type == 'get' else requests.post(uri, json=task_data.model_dump())
    return response, expected_data


@pytest.mark.parametrize('test_name', [resource.name
                                        for resource in files(settings.parameterized_tests_dir).iterdir()])
def test_perform_tasks(app_container: object, test_name: str) -> None:
    """
    Testing various task using the files in app.cfg.cfg_parameterized_tests as an input (parameterized test)
    :param app_container: the docker container in which the app resides in
    :param test_name: test name as taken from the file names resides in tests.cfg.cfg_parameterized_tests folder
    :return: no return - assertion is made on the api response
    """
    cfg_data: FullRequest = get_param_data(test_name=test_name) # get the test data
    resp: Tuple[Response, ReturnData] = shared_test_logic(cfg_data)
    response, expected_data = resp
    res_json = response.json()
    logger.info(F"response from api-client: {resp}")
    # Check that the API response is as expected
    assert response.status_code == expected_data.status_code, \
        F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, {res_json.get('result')}.\n"
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res_json.get('result') == expected_data.return_value, (F"\nwrong response val: {res_json.get('result')}\n"
                                                                 F"expected: {expected_data.return_value}\n")


# @pytest.mark.slow
def test_non_parameterized_example(app_container: object, load_test_data: FullRequest) -> None:
    """
    Testing a specific task using the files in app.cfg.cfg_non_parameterized_tests as input
    :param app_container: the docker container in which the app resides in
    :param load_test_data: the test data
    :return: no return. assertion is made on the api response
    """
    resp: Tuple[Response, ReturnData] = shared_test_logic(load_test_data)
    response, expected_data = resp
    res_json = response.json()
    logger.info(F"response from api-client: {resp}")
    # Check that the API response is as expected
    assert response.status_code == expected_data.status_code, \
        F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, {res_json.get('result')}.\n"
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res_json.get('result') == expected_data.return_value, (F"\nwrong response val: {res_json.get('result')}\n"
                                                                 F"expected: {expected_data.return_value}\n")

