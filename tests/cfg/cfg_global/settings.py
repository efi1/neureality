from time import sleep

cfg_tests_dir = 'tests.cfg.cfg_tests'
image_name = 'efiradware/reverse-restore-app:2.0.1'
external_port = 8000  # the default port which FastAPI app (Uvicorn) runs inside the container
base_url = f'http://localhost:{external_port}'
ports = {"8000/tcp": external_port}
success_resp = 200
container_timeout = 10
sleep_time = 1
