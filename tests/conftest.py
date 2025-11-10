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


def resolve_placeholders(value: str) -> str:
    """Resolve {key} placeholders using values from settings."""
    try:
        return value.format(**{
            k: getattr(settings, k)
            for k in dir(settings)
            if not k.startswith("_")
        })
    except Exception:
        return value


def pytest_addoption(parser):
    for variable in dir(settings):
        if variable.startswith("_"):
            continue
        value = getattr(settings, variable)
        resolved = resolve_placeholders(str(value)) if isinstance(value, str) else value
        parser.addoption(
            f"--{variable}",
            action="store",
            default=resolved,
            help=f"Override {variable} (default: {resolved})"
        )

@pytest.fixture(scope="session")
def effective_settings(request):
    config = {}
    for variable in dir(settings):
        if variable.startswith("_"):
            continue
        cli_value = request.config.getoption(f"--{variable}")
        config[variable] = cli_value
    return config


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
def docker_client():
    try:
        client = docker.from_env()
        return client
    except (docker.errors.DockerException, OSError) as e:
        pytest.skip(f"Skipping tests because Docker is not available: {e}")


def build_local_image(client, image_name, dockerfile_path, dockerfile_name):
    print("Building Docker image...")
    build_context = Path(__file__).parent.parent
    if not build_context.is_dir():
        raise ValueError(f"Build context directory does not exist: {build_context}")
    # Check if Dockerfile exists inside the build context
    dockerfile_full_path = build_context.joinpath(dockerfile_path, dockerfile_name)
    if not dockerfile_full_path.is_file():
        raise ValueError(f"Dockerfile not found at: {dockerfile_full_path}")
    dockerfile_parent_path = build_context.joinpath(dockerfile_path)

    image, logs = client.images.build(
        path=str(dockerfile_parent_path),dockerfile=dockerfile_name,
        tag=image_name,
        rm=True,         # remove intermediate containers
        forcerm=True     # force removal even if build fails
    )

    for line in logs:
        logger.info(line.get('stream', '').strip())
    return image


@fixture(scope="session")
def app_container(docker_client, request):

    client = docker_client
    app_net_name = get_docker_network.get_effective_network(client)

    image_id = None
    image_name = request.config.getoption('image_remote_name')
    use_local_image = request.config.getoption('use_local_image')

    if use_local_image:
        dockerfile_path = request.config.getoption('dockerfile_path')
        dockerfile_name = request.config.getoption('dockerfile_name')
        built_image = build_local_image(client, image_name, dockerfile_path, dockerfile_name)
        image_id = built_image.id
        image_name = built_image.tags[0] if built_image.tags else image_id

    # start the container with auto_remove - delete the container after it stops
    container = client.containers.run(
        image_id or image_name,
        ports=request.config.getoption('ports'),
        detach=True,
        auto_remove=True,
        network=app_net_name,
        name=request.config.getoption('container_name')
    )

    container_timeout = request.config.getoption('container_timeout')
    container_sleep_time = request.config.getoption('sleep_time')
    print('')

    try:
        if not is_container_healthy(container, container_timeout, container_sleep_time):
            raise RuntimeError(F"App container did not become available after {container_timeout} sec.")

        yield container

        collect_container_logs(container, logger)

    finally: # cleanup - stop the container at the end of tests, remove is done automatically (auto_remove)

        try:
            container.stop()
            logger.info("Container stopped successfully")

        except Exception as e:
            logger.info("Container already stopped or removed:", e)

        # Remove the local image if it was built
        if use_local_image and image_id:
            try:
                client.images.remove(image=image_id, force=True)
                logger.info(f"Local image {image_id} removed successfully")
            except Exception as e:
                logger.warning(f"Failed to remove local image {image_id}: {e}")

        remove_exited_containers(request=request)
        remove_dangling_images(request=request)


def remove_exited_containers(request):
    docker_client = request.getfixturevalue("docker_client")
    for container in docker_client.containers.list(all=True, filters={"status": "exited"}):
        try:
            container.remove(force=True)
            logger.info(f"Removed exited container: {container.name}")
        except Exception as e:
            logger.warning(f"Failed to remove container {container.name}: {e}")

def remove_dangling_images(request):
    docker_client = request.getfixturevalue("docker_client")
    for image in docker_client.images.list(filters={"dangling": True}):
        try:
            docker_client.images.remove(image.id, force=True)
            logger.info(f"Removed dangling image: {image.id}")
        except Exception as e:
            logger.warning(f"Failed to remove image {image.id}: {e}")


def read_json_file(path: Path) -> dict:
    """  Read from json file """
    with open(path) as file:
        data = json.loads(file.read())
    return data


def share_get_data_logic(request, cfg_dir: str, test_name: str) -> ObjectLikeData:
    """shared logic in reading the cfg test data and convert it to a class data object  """
    cfg_file: Path | Traversable = files(cfg_dir).joinpath(test_name)
    if cfg_file.exists():
        json_params = read_json_file(cfg_file)
        base_url = request.config.getoption('base_url_inner_container') if get_docker_network.is_running_in_container() \
        else request.config.getoption('base_url')
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
    cfg_dir = request.config.getoption('non_parameterized_tests_dir')
    return share_get_data_logic(request, cfg_dir, f'{test_name}.json')


def get_param_data(request, test_name: str) -> ObjectLikeData:
    """
    Rendering config data out of a template cfg file - for parameterized test
    :param request: a built-in fixture that provides access to the context of the test function
    :param test_name: name as given by test when it is being executed
    :return: tests data as a class object
    """
    logging.info(F"load cfg_data for {test_name.split('.')[0]}")
    cfg_dir = request.config.getoption('parameterized_tests_dir')
    return share_get_data_logic(request, cfg_dir, test_name)


def param_extract_number(filename):
    match = re.search(r'test_(\d+)', filename)
    return int(match.group(1)) if match else float('inf')


def get_sorted_param_files(config):
    test_dir = config.getoption('parameterized_tests_dir')
    return sorted(
        [resource.name for resource in files(test_dir).iterdir()],
        key=param_extract_number
    )

"""pytest_generate_tests function is a hook that allows you to dynamically parameterize tests at collection time, 
rather than using @pytest.mark.parametrize directly in the test file.
For any test function that uses a fixture or parameter named test_name, parameterize it with sorted_files.
"""
def pytest_generate_tests(metafunc):
    if 'test_name' in metafunc.fixturenames:
        sorted_files = get_sorted_param_files(metafunc.config)
        metafunc.parametrize('test_name', sorted_files, scope='class')

