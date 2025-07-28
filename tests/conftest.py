"""Shared fixtures."""
import logging
from importlib.resources import files
from _pytest.fixtures import fixture
import json
from starlette.testclient import TestClient
from tests.cfg.cfg_global import settings
import app.clients.fastapi.tasks_base as tasks_base


@fixture(scope="session")
def api_client():
    """
    start the test's client.
    :return: test client.
    """
    logging.info('initiate the FastAPI client')
    client = TestClient(tasks_base.app)
    yield client


def cfg_get_data(test_name: str) -> dict:
    """
    Rendering config data out of a template cfg file
    :param test_name:
    :return: dict test's data
    """
    def _load_test_params(path):
        with open(path) as file:
            data = json.loads(file.read())
        return data

    logging.info(F"load cfg_data for {test_name.split('.')[0]}")
    cfg_template_dir = settings.cfg_tests_dir
    cfg_template_file = files(cfg_template_dir).joinpath(test_name)
    if cfg_template_file.exists():
        return _load_test_params(cfg_template_file)

