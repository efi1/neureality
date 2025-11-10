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


def get_host_network(docker_client):
    """If running on host, return default bridge network."""
    try:
        bridge = docker_client.networks.get("bridge")
        return bridge.name
    except docker.errors.NotFound:
        return None


def get_effective_network(docker_client, network_name="bridge"):
    """
    Return the given network name if running in a container and it's valid.
    Otherwise, return the default host network (usually 'bridge').
    """
    if is_running_in_container():
        return network_name
    else:
        logger.info("++++ running on host, using default network")
        return get_host_network(docker_client)

