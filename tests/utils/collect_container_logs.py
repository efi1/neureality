import subprocess


def get_container_logs(container_name: str) -> str:
    """ read the container logs after tests completed """
    try:
        output = subprocess.check_output(["docker", "logs", container_name])
        return output.decode()
    except subprocess.CalledProcessError as e:
        return f"Error getting logs: {e.output.decode()}"


def get_filtered_container_logs(container_name, exclude_keywords=None, lines=200):
    if exclude_keywords is None:
        exclude_keywords = []

    try:
        output = subprocess.check_output(
            ["docker", "logs", "--tail", str(lines), container_name]
        ).decode()

        # filter out non relevant lines
        filtered_lines = [
            line for line in output.splitlines()
            if not any(kw in line for kw in exclude_keywords)
        ]

        return "\n".join(filtered_lines)

    except subprocess.CalledProcessError as e:
        return f"Error getting logs: {e.output.decode()}"


def collect_container_logs(app_container: object, logger: object, exclude_keywords: None = None) -> None:
    if exclude_keywords is None:
        exclude_keywords = ['health']
    container_name = app_container.name
    logs = get_filtered_container_logs(container_name, exclude_keywords=exclude_keywords)
    logger.info(f'==== FastAPI container logs ====\n{logs}')