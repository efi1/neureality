## 🐳 Python HTTP App with Docker + Pytest

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


<br>🚀 Application

A Docker container running a Python HTTP application built with FastAPI.

A pre-built Docker image is available and automatically pulled from DockerHub when tests are executed.

The image is built using a Dockerfile located at the project root.

The application source code used in the image is located under the /app directory.

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


### 🐳 Running the Docker App

Running the Docker container is handled automatically before tests begin.

This is managed inside the `conftest.py` file using a `pytest` fixture named `app_container`.

The fixture:

- Starts the FastAPI application in a Docker container using the provided image.
- Calls the helper function `is_container_healthy`, which waits for a defined period of time.
- Validates the container health by hitting the `/health` endpoint.

If the container becomes healthy within the timeout window, the tests will proceed.  
If not, the test run will fail early, ensuring the created container is removed.

When the tests end, the container is stopped and removed.

### 🧪 Tests Structure
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


