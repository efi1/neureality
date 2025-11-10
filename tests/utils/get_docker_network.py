import logging
import os
import docker
import docker.errors


logger = logging.getLogger(__name__)


def is_running_in_container():
    """
    Detect if running inside a Docker (or containerized) environment.
    Returns True if inside a container, False otherwise.
    """
    # Check for the /.dockerenv file
    if os.path.exists("/.dockerenv"):
        return True

    # Check /proc/1/cgroup for docker/kubepods indicators
    try:
        with open("/proc/1/cgroup", "rt") as f:
            for line in f:
                if "docker" in line or "kubepods" in line:
                    return True
    except FileNotFoundError:
        pass

    return False


def get_self_container_id():
    """Return current container ID (short)."""
    return os.environ.get("HOSTNAME")


def get_self_network(docker_client):
    """If running in container, return its first network."""
    self_id = get_self_container_id()
    logger.info(f'++++ HOSTNAME is {self_id}')

    if not self_id:
        return None

    try:
        logger.info('++++ getting network name')
        container = docker_client.containers.get(self_id)  # works with short ID
        logger.info(f'++++ container: {container}')
        networks = container.attrs["NetworkSettings"]["Networks"]
        logger.info(f'++++ networks: {networks}')
        return list(networks.keys())[0] if networks else None
    except docker.errors.NotFound as e:
        logger.info(f'++++ Error om get_self_network: {e}')
        return None


def get_host_network(docker_client):
    """If running on host, return default bridge network."""
    try:
        bridge = docker_client.networks.get("bridge")
        return bridge.name
    except docker.errors.NotFound:
        return None


def get_effective_network(docker_client):
    """Return network name depending on environment."""
    if is_running_in_container():
        net = get_self_network(docker_client)
        logger.info(f'++++ running within a container, net is {net}')
        if net:
            return net
    return get_host_network(docker_client)

