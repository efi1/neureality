"""Shared fixtures."""
import ast
import time
import logging
import json
import docker
from typing import List
from pathlib import Path
from importlib.abc import Traversable
from _pytest.fixtures import fixture
from importlib.resources import files
from jinja2 import FileSystemLoader, Environment
from tests.utils.data_to_obj import ObjectLikeData, data_object
from tests.utils.collect_container_logs import collect_container_logs


logger = logging.getLogger(__name__)

CFG_DIR = Path().absolute().joinpath('tests', 'cfg')
GLOBAL_CFG_DIR: Path = CFG_DIR.joinpath('cfg_global')
GLOBAL_CFG_FILE: Path = Path(GLOBAL_CFG_DIR).joinpath("global_config.json")
CFG_TEST_DIR: List[Path] = [CFG_DIR.joinpath(f) for f in ['cfg_non_parameterized_tests', 'cfg_parameterized_tests']]


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


@fixture(scope="session")
def app_container(global_data_object):
    client = docker.from_env()

    # start the container with auto_remove - delete the container after it stops
    container = client.containers.run(
        global_data_object.image_name,
        ports=ast.literal_eval(global_data_object.ports),
        detach=True,
        auto_remove=True
    )

    try:
        if not is_container_healthy(container, global_data_object.container_timeout, global_data_object.sleep_time):
            raise RuntimeError(F"App container did not become available after {global_data_object.container_timeout} sec.")

        yield container

        collect_container_logs(container, logger, global_data_object.excluded_keywords)

    finally: # cleanup - stop the container at the end of tests, remove is done automatically (auto_remove)

        try:
            container.stop()
            logger.info("Container stopped successfully")

        except Exception as e:
            logger.info("Container already stopped or removed:", e)


def read_json_file(path: Path) -> dict:
    """  Read from json file """
    with open(path) as file:
        data = json.loads(file.read())
    return data


@fixture(scope="session")
def global_dict_data(file=GLOBAL_CFG_FILE):
    return read_json_file(file)

@fixture(scope="session")
def global_data_object(global_dict_data) -> ObjectLikeData:
    """ Map dictionary keys and values to class attributes"""
    return data_object(global_dict_data)


@fixture(scope="function")
def load_test_data(request, global_dict_data: dict) -> ObjectLikeData:
    """
    Rendering config data out of a template cfg file - for unparameterized test
    :param request: fixture utility to get the test name
    :param global_dict_data: project's global_cfg data
    :return: tests data as a class object
    """
    test_name = request.node.name
    return share_get_data_logic(test_name, global_dict_data)


def get_cfg_template(test_name, cfg_test_dir: List[Path]):
    """get a template which required """
    template_loader = FileSystemLoader(searchpath=cfg_test_dir)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(f'{test_name}.json')
    return template


def is_cfg_file(test_name, cfg_test_dir) -> bool:
    """ check if file exist in the cfg folders"""
    cfg_test_name = F'{test_name}.json'
    for path in cfg_test_dir:
        cfg_test_path = path.joinpath(cfg_test_name)
        if cfg_test_path.exists():
            return True
    return False

def share_get_data_logic(test_name: str, global_dict_data: dict) -> ObjectLikeData:
    """shared logic in rendering the cfg test data """
    is_file_exist = is_cfg_file(test_name, CFG_TEST_DIR)
    if not is_file_exist:
        raise ValueError(f'Test {test_name} has no data, executing test with no data file')
    # create a template which required for rendering out of the cfg test file
    test_template = get_cfg_template(test_name, CFG_TEST_DIR)
    # render the template together with the global data file
    cfg_test_rendered_data = test_template.render(global_dict_data)
    # convert the rendered data to a dict in order to convert it to a class object
    dict_test_rendered_data = json.loads(cfg_test_rendered_data)
    return data_object(dict_test_rendered_data)


def get_param_data(test_name: str, global_dict_data: dict) -> ObjectLikeData:
    """
    Rendering config data out of a template cfg file - for parameterized test
    :param global_dict_data: global data of dict structure
    :param test_name: name as given by test when it is being executed
    :return: test data as a class object
    """
    logging.info(F"load cfg_data for {test_name}")
    return share_get_data_logic(test_name, global_dict_data)


def pytest_generate_tests(metafunc):

    """dynamically creates a separate test run for each file in a specified
    directory for test functions that use the test_name fixture"""

    # Check if the test function uses the 'test_name' fixture
    if 'test_name' in metafunc.fixturenames:
        # Load configuration from a global JSON file
        file_path = GLOBAL_CFG_FILE
        config = read_json_file(file_path)
        # Access the directory where parameterized test files are located
        param_dir = files(config['parameterized_tests_dir'])
        # Collect all file names (without extensions) in that directory
        test_names = [p.name.split('.')[0] for p in param_dir.iterdir() if p.is_file()]
        # Dynamically parameterize 'test_name' for the test function
        metafunc.parametrize('test_name', test_names)

