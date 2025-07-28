from time import sleep

cfg_tests_dir = 'tests.cfg.cfg_tests'
image_name = 'efiradware/reverse-restore-app:latest'
app_uri = 'http://localhost:8000/'
ports = {"8000/tcp": 8000}
success_resp = 200
app_not_available_msg = 'reverse-restore-app is not available'
container_run_waiting_time = 10
sleep_time = 1
