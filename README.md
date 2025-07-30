# Python HTTP App with Docker + Pytest

<br>This project includes:

A Python-based HTTP application running in a Docker container

Two main RESTful APIs (/reverse, /restore) and another one /health to test the running container health status

A testing framework built with pytest that:

Starts and stops the Docker container automatically

Verifies API behavior

Outputs test results in JUnit format

Supports easy extension with more tests

<br> 📁 Project Structure

    .
    ├── app/
    │   ├── app_requirements.txt             # Requirements specific to the app
    │   └── clients/
    │       └── fastap/
    │           ├── routes/
    │           │   └── schemas.py           # Schema definitions for API routes
    │           ├── schemas.py               # Shared schemas
    │           └── tasks_base.py            # Contains: app = FastAPI()
    │
    ├── tests/
    │   ├── cfg/
    │   │   ├── cfg_global/                     # Global test config
    │   │   ├── cfg_non_parameterized_tests/    # Data for a single test run
    │   │   └── cfg_parameterized_tests/        # Parametrized test cases
    │   │
    │   ├── utils/                           # Used in conftest
    │   │   └── [utility files]
    │   │
    │   ├── conftest.py                      # Shared pytest fixtures (e.g., Docker setup)
    │   └── test_tasks.py                    # Tests for /reverse and /restore endpoints
    │
    ├── pytest.ini                           # Pytest config 
    ├── setup.py                             # Package setup 
    ├── Dockerfile                           # Builds and runs the FastAPI app in a container


## Application

A Docker container running a Python HTTP application built with FastAPI.

A pre-built Docker image is available and automatically pulled from DockerHub when tests are executed.

The image is built using a Dockerfile located at the project root.

The application source code used in the image is located under the /app directory (app is under the root project).

The application exposes the following four RESTful APIs:

(You can view and test them interactively at: http://localhost:8000/docs)


✅ POST /reverse

Request JSON format:

{ 
"task_name": "string reverse", 
"task_parameters": { "given string": "The quick brown fox jumps over the lazy dog" 
}

Response: 
{
    "result": "dog lazy the over jumps fox brown quick The"
}

✅ GET /restore

Returns the last result produced by the /reverse endpoint.

Response:
{
    "result": "dog lazy the over jumps fox brown quick The"
}

✅ GET /

Takes no parameters and returns a welcome message.

Response:
{
    "result": "Welcome to reverse and restore handler"
}

✅ GET /health

Used to verify that the Docker container is running and healthy after deployment.

Response:
{
    "status": "ok"
}


## Running the Docker App

Running the Docker container is handled automatically before tests begin.

This is managed inside the `conftest.py` file using a `pytest` fixture named `app_container`.

The fixture:

- Starts the FastAPI application in a Docker container using the provided image.
- Calls the helper function `is_container_healthy`, which waits for a defined period of time.
- Validates the container health by hitting the `/health` endpoint.

If the container becomes healthy within the timeout window, the tests will proceed.  
If not, the test run will fail early, ensuring the created container is removed.

When the tests end, the container is stopped and removed.

## Tests Structure
There are two types of tests supported:

- Parameterized tests

- Non-parameterized tests (also called unparameterized tests)

<br>📂 Test Data Location

Test data is stored under the tests/cfg folder, which contains three subfolders:

__cfg_global/__
Contains global settings (__settings.py__) and configuration files, including:

Docker image name

Base URL where the app is running

External port the container exposes

Paths to parameterized and non-parameterized test data files

__cfg_parameterized_tests/__
Contains data files for parameterized test cases.

__cfg_non_parameterized_tests/__
Contains data files for non-parameterized (single run) test cases.


### Adding a Test
The test suite supports both parameterized and non-parameterized test types.
Each is configured by adding a JSON file in the appropriate directory under tests/cfg.


✅ Adding a Parameterized Test
* Create a new JSON file under:
tests/cfg/cfg_parameterized_tests/

* The file name can be arbitrary, but it must have a .json extension.

* Once added, the test data will be picked up automatically by the existing parameterized test in test_tasks.py.

* The test function is already implemented and accepts two inputs:

app_container: the running Docker container (provided via a fixture).

test_name: the name of the test case (taken from the JSON filename).


        @pytest.mark.parametrize('test_name', [
            resource.name
            for resource in files(settings.parameterized_tests_dir).iterdir()
        ])
        def test_perform_tasks(app_container: object, test_name: str) -> None:
            ...


📌 Note: There is no need to manually register new test functions.
Each JSON file in cfg_parameterized_tests/ will be executed automatically.

✅ Adding a Non-Parameterized Test
* Create a new JSON file under:
tests/cfg/cfg_non_parameterized_tests/

* The file name must start with the word "test_" and have a .json extension, so that pytest recognizes it.

* In test_tasks.py, add a function with the same name as the JSON file, but without the .json extension.

Example:
If the file is named test_example_1.json, define a function:

    def test_example_1(app_container, load_test_data):
        ...

* The test function must accept the following arguments:

app_container: the Docker container running the app.

load_test_data: fixture that automatically loads the corresponding JSON file.

## Test Data Structure

Each test case is defined in a JSON file with the following structure:

    {
        "task_data": {
            "task_name": "string reverse",
            "task_parameters": {
                "given string": "<Text to be reversed>"
            },
            "request_type": "post"
        },
        "return_data": {
            "return_value": "<the reversed text>",
            "status_code": 200,
            "validate_resp_val": true
        },
        "api_path": "/api/task/reverse"
    }

### Required Structure
The JSON file must include three main keys:

- "task_data" — describes the request to send

- "return_data" — describes the expected response

- "api_path" — the endpoint to target

Each section must include the following subkeys:

✅ task_data must contain:
- task_name (mandatory)

- task_parameters (can be null or an empty object, but key must exist)

- request_type (mandatory)

✅ return_data must contain:
- return_value (can be null or an empty string, but key must exist)

- status_code (mandatory)

- validate_resp_val (mandatory)

✅ api_path:
Must be a valid endpoint string (mandatory)

#### Negative Test Examples

You can review intentionally misconfigured cases under:
tests/cfg/cfg_parameterized_tests/

These negative tests demonstrate what happens when required keys are missing or malformed — they are designed to fail and validate error handling in the API.


## Performance Testing 
Performance tests are not yet implemented.

A performance test type could simulate a group of users sending simultaneous GET and POST requests to the FastAPI application.

### Conceptual behavior:
Launch multiple threads or asynchronous workers to hit /reverse and /restore endpoints concurrently.
Measure:  Response times, Server throughput, Error rates under load


## Loading Test Data
Test input data is stored in JSON files and automatically loaded into the test functions.

✅ Parameterized Tests
In parameterized tests (e.g. test_perform_tasks), the first line inside the test function calls:

test_data = get_param_data(test_name)
get_param_data is defined in conftest.py. It:

- Locates the correct test JSON file by its name (file is located under cfg_non_parameterized_tests/).

- Reads and parses the file.

- Returns a structured object containing all required data for the test.

✅ Unparameterized Tests
In non-parameterized (individual) tests, data is automatically provided by the load_test_data fixture:

    def test_example_1(app_container, load_test_data):
        ...
    
The fixture load_test_data:
- Uses pytest’s request.node.name to dynamically identify which JSON file to load — based on the name of the test function.

- Locates the matching JSON file in cfg_non_parameterized_tests/

- Loads and returns the test data to the function

📌 Both methods ensure each test receives the correct input without hardcoding paths or filenames.

## JUnit Test Report
A JUnit-compatible XML report is automatically generated during test execution.

* Where it's saved:
The report file is created in a directory called:
./reports/ 

### Automatic Generation

The pytest.ini includes the following setting to always generate the JUnit report:

    [pytest]    
    addopts = --junitxml=reports/test_results.xml
    This ensures that every test run will produce a report file at:
    reports/test_results.xml

### Manual Trigger (Optional)

You can also run tests and explicitly generate the JUnit file by including the --junitxml flag:

    python -m pytest --junitxml=reports/test_results.xml
    
- You should remove the definition from pytest.ini (in case of running it manually).

## Logging

Test execution logs are generated automatically and saved to the ./logs/ directory.
- Logging behavior is configured in the pytest.ini file.


## Before running the tests:
* Clone it from GitHub to your local environment.

* Create a Python virtual environment and activate it (instructions can be found later in the text below).

* Upgrade the pip package by:

    python -m pip install --upgrade pip

* Install setup.py by:


      python -m pip install . (include the dot at the end) — see elaboration below.


### The setup.py file 

* Installs your package into the virtual environment.

* Registers your project source directory (e.g. app/) as an importable module.

* Resolves internal imports using dot notation, like:

    from app.clients.fastap.routes import tasks


## To run the tests via pytest (for both Windows and Linux)

* First, install the setup.py as mentioned before.

To run the test via CLI, while in the __project root__ (and virtualenv is activated), type:

    python -m pytest

### To create a virtualenv (and activate it):

#### On Windows:
* Create a virtualenv:

    c:\path\to\python -m venv c:\path\to\myenv\venv

Or while residing in the root of the Python project directory (assuming python.exe is callable):

    python -m venv .\venv

* Activate the virtualenv:
While residing in the root of the Python project directory:
.\venv\Scripts\Activate.ps1

#### On Linux (Debian/Ubuntu):
* Update your Ubuntu environment first:
  
    sudo apt-get update (you may add the flag: --fix-missing if problems persist)

* Install venv package:

    sudo apt install python3-venv

* Create the virtualenv:
  
    python -m venv /mnt/d/Neureality/venv

* To activate virtual env (Linux):
While residing in the root of the Python project directory:

    source venv/bin/activate

* To exit virtual env (for both Linux and Windows):
Type: deactivate

