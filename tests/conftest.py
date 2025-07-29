"""Shared fixtures."""
import json
import time
import logging
import docker
from _pytest.fixtures import fixture
from importlib.resources import files
from tests.cfg.cfg_global import settings
from tests.utils.collect_container_logs import collect_container_logs
from tests.utils.data_to_obj import FullRequest

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


@fixture(scope="session")
def app_container():
    client = docker.from_env()

    # start the container with auto_remove - delete the container after it stops
    container = client.containers.run(
        settings.image_name,
        ports=settings.ports,
        detach=True,
        auto_remove=True
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
