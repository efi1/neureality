"""Shared fixtures."""
import re
import time
import logging
import json
import pytest
import docker
import docker.errors
from pathlib import Path
from importlib.abc import Traversable
from _pytest.fixtures import fixture
from importlib.resources import files
from tests.utils import get_docker_network
from tests.cfg.cfg_global import settings
from tests.utils.data_to_obj import ObjectLikeData, data_object
from tests.utils.collect_container_logs import collect_container_logs


logger = logging.getLogger(__name__)


def is_container_healthy(container: object, timeout_seconds: int, interval: int = 1, elapsed: int = 0) -> bool:
    # Is the container in a healthy state after the wait period
    while elapsed < timeout_seconds:
        container.reload()
        status = container.attrs.get("State", {}).get("Health", {}).get("Status")
        if status == "healthy":
            return True
        elif status in ("unhealthy", "exited"):
            break
        time.sleep(interval)
        elapsed += interval
    return False


def get_docker_client():
    try:
        client = docker.from_env()
        return client
    except (docker.errors.DockerException, OSError) as e:
        pytest.skip(f"Skipping tests because Docker is not available: {e}")


@fixture(scope="session")
def app_container():

    client = get_docker_client()
    app_net_name = get_docker_network.get_effective_network(client)

    # start the container with auto_remove - delete the container after it stops
    container = client.containers.run(
        settings.image_name,
        ports=settings.ports,
        detach=True,
        auto_remove=True,
        network=app_net_name,
        name=settings.container_name
    )

    try:
        if not is_container_healthy(container, settings.container_timeout, settings.sleep_time):
            raise RuntimeError(F"App container did not become available after {settings.container_timeout} sec.")

        yield container

        collect_container_logs(container, logger)

    finally: # cleanup - stop the container at the end of tests, remove is done automatically (auto_remove)

        try:
            container.stop()
            logger.info("Container stopped successfully")

        except Exception as e:
            logger.info("Container already stopped or removed:", e)

def get_base_url():
    return settings.base_url.format(host = settings.container_name) if get_docker_network.is_running_in_container() \
        else settings.base_url.format(host = settings.host)


def read_json_file(path: Path) -> dict:
    """  Read from json file """
    with open(path) as file:
        data = json.loads(file.read())
    return data


def share_get_data_logic(cfg_dir: str, test_name: str) -> ObjectLikeData:
    """shared logic in reading the cfg test data and convert it to a class data object  """
    cfg_file: Path | Traversable = files(cfg_dir).joinpath(test_name)
    if cfg_file.exists():
        json_params = read_json_file(cfg_file)
        base_url = get_base_url()
        json_params['base_url'] = base_url
        return data_object(json_params) # create an object with the test data
    raise ValueError(f'Test {test_name} has no data – please check the test input file')


@fixture(scope="function")
def load_test_data(request) -> ObjectLikeData:
    """
    Rendering config data out of a template cfg file - for non parameterized test
    :return: tests data as a class object
    """
    test_name = request.node.name
    logging.info(F"load cfg_data for {test_name}")
    cfg_dir = settings.non_parameterized_tests_dir
    return share_get_data_logic(cfg_dir, f'{test_name}.json')


def get_param_data(test_name: str) -> ObjectLikeData:
    """
    Rendering config data out of a template cfg file - for parameterized test
    :param test_name: name as given by test when it is being executed
    :return: tests data as a class object
    """
    logging.info(F"load cfg_data for {test_name.split('.')[0]}")
    cfg_dir = settings.parameterized_tests_dir
    return share_get_data_logic(cfg_dir, test_name)


def param_extract_number(filename):
    match = re.search(r'test_(\d+)', filename)
    return int(match.group(1)) if match else float('inf')


def sorted_param_files():
    return sorted([resource.name for resource in files(settings.parameterized_tests_dir).iterdir()],
                  key=param_extract_number)
