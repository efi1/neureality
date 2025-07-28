"""Shared fixtures."""
import json
import time
import logging
import docker
import requests
from _pytest.fixtures import fixture
from importlib.resources import files
from tests.cfg.cfg_global import settings
from tests.utils.data_to_obj import FullRequest


@fixture(scope="session")
def app_container():
    client = docker.from_env()

    # Launch a container based on the app image
    container = client.containers.run(
        settings.image_name,
        ports=settings.ports,
        detach=True
    )

    # wait for the container to be launched
    for _ in range(settings.container_run_waiting_time):
        try:
            response = requests.get(settings.app_uri)
            if response.status_code == settings.success_resp:
                break
        except requests.ConnectionError:
            time.sleep(settings.sleep_time)
    else:
        container.stop()
        container.remove()
        raise RuntimeError(settings.app_not_available_msg)

    yield container

    # teardown container at the end of tests
    container.stop()
    container.remove()


def load_test_params(path) -> dict:
    """
    Read from cfg_test file and get the test's parameters
    :return:  test's parameters
    """
    with open(path) as file:
        data = json.loads(file.read())
    return data


def cfg_get_data(test_name: str) -> object | None:
    """
    Rendering config data out of a template cfg file
    :param test_name:
    :return: dict test's data
    """
    logging.info(F"load cfg_data for {test_name.split('.')[0]}")
    cfg_template_dir = settings.cfg_tests_dir
    cfg_template_file = files(cfg_template_dir).joinpath(test_name)
    if cfg_template_file.exists():
        json_params =  load_test_params(cfg_template_file)
        return FullRequest(**json_params)
    return None

