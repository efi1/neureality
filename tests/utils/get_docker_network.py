import logging
import os
import docker
import docker.errors

logger = logging.getLogger(__name__)

def is_running_in_container():
    """Detect if running inside a Docker (or containerized) environment."""
    if os.path.exists("/.dockerenv"):
        return True

    try:
        with open("/proc/1/cgroup", "rt") as f:
            for line in f:
                if "docker" in line or "kubepods" in line:
                    return True
    except FileNotFoundError:
        pass

    return False

def get_self_container_id():
    """Return current container ID (short or full)."""
    try:
        with open("/proc/self/cgroup", "rt") as f:
            for line in f:
                parts = line.strip().split('/')
                for part in parts:
                    if len(part) == 64:  # full container ID
                        return part
                    elif len(part) == 12:  # short ID
                        return part
    except Exception as e:
        logger.warning(f"Could not read container ID: {e}")

    return None

def get_self_network(docker_client):
    """If running in container, return its first network."""
    self_id = get_self_container_id()
    logger.info(f'++++ Container ID is {self_id}')

    if not self_id:
        return None

    try:
        container = docker_client.containers.get(self_id)
        networks = container.attrs["NetworkSettings"]["Networks"]
        logger.info(f'++++ networks: {networks}')
        return list(networks.keys())[0] if networks else None
    except docker.errors.NotFound as e:
        logger.info(f'++++ Error on get_self_network: {e}')
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