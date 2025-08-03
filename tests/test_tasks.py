from typing import Tuple
import pytest
import requests
from requests import Response
from tests.cfg.cfg_global import settings
from importlib.resources import files
from conftest import get_param_data, logger
from tests.utils.data_to_obj import data_object, ObjectLikeData, object_dump


def shared_test_logic(cfg_data: ObjectLikeData) -> Tuple[Response, ObjectLikeData]:
    task_data = cfg_data.task_data # request data
    req_type = task_data.request_type # GET or POST request
    expected_data = cfg_data.return_data # expected response of the request
    api_path = cfg_data.api_path
    uri = f'{settings.base_url}{api_path}'
    log_msg = f'calling get {uri}' if req_type == 'get' else f'calling post {uri}, data: {object_dump(task_data)}'
    logger.info(F"api-client request: {log_msg}")
    # execute the api call
    response = requests.get(uri) if req_type == 'get' else requests.post(uri, json=object_dump(task_data))
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
    cfg_data: data_object = get_param_data(test_name=test_name) # get the test data
    resp: Tuple[Response, ObjectLikeData] = shared_test_logic(cfg_data)
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


def test_negative_422_missing_required_field(app_container: object, load_test_data: ObjectLikeData) -> None:
    """
    A POST request with the task_name required field missing from the request body - http 422 Unprocessable Entity
    :param app_container: the docker container in which the app resides in
    :param load_test_data: the test data
    """
    resp: Tuple[Response, ObjectLikeData] = shared_test_logic(load_test_data)
    response, expected_data = resp
    res_json = response.json()
    logger.info(F"response from api-client: {resp}")
    # Check that the API response is as expected
    assert response.status_code == expected_data.status_code, \
        (F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, "
         F"Error msg: {res_json.get('detail')[0].get('msg') if not res_json.get('result') else res_json.get('result')}.\n")
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res_json.get('result') == expected_data.return_value, (F"\nwrong response val: {res_json.get('result')}\n"
                                                                 F"expected: {expected_data.return_value}\n")


def test_negative_404_missing_string_input(app_container: object, load_test_data: ObjectLikeData) -> None:
    """  A POST request with the given string value missing from the request body - http 404 Not Found """
    resp: Tuple[Response, ObjectLikeData] = shared_test_logic(load_test_data)
    response, expected_data = resp
    res_json = response.json()
    logger.info(F"response from api-client: {resp}")
    # Check that the API response is as expected
    # assert response.status_code == expected_data.status_code, \
    #     (F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, "
    #      F"Error msg: {res_json.get('detail')[0].get('msg') if not res_json.get('result') else res_json.get('result')}.\n")
    assert response.status_code == expected_data.status_code, \
        (F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, "
         F"Error msg: {res_json.get('result')}.\n")
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res_json.get('result') == expected_data.return_value, (F"\nwrong response val: {res_json.get('result')}\n"
                                                                 F"expected: {expected_data.return_value}\n")


def test_negative_405_wrong_request_method(app_container: object, load_test_data: ObjectLikeData) -> None:
    """  A GET request sent to an API path that expects POST """
    resp: Tuple[Response, ObjectLikeData] = shared_test_logic(load_test_data)
    response, expected_data = resp
    res_json = response.json()
    logger.info(F"response from api-client: {resp}")
    # Check that the API response is as expected
    assert response.status_code == expected_data.status_code, \
        (F"\nExpected status code: {expected_data.status_code}\nactual: {response.status_code}, "
         F"Error msg: {res_json.get('detail')[0].get('msg') if not res_json.get('result') else res_json.get('result')}.\n")
    # Check that the API response's content is as expected
    if expected_data.validate_resp_val:
        assert res_json.get('result') == expected_data.return_value, (F"\nwrong response val: {res_json.get('result')}\n"
                                                                 F"expected: {expected_data.return_value}\n")