🐳 Python HTTP App with Docker + Pytest

This project includes:

A Python-based HTTP application running in a Docker container

Two main RESTful APIs (/reverse, /restore) and another one /health to test the running container health status

A testing framework built with pytest that:

Starts and stops the Docker container automatically

Verifies API behavior

Outputs test results in JUnit format

Supports easy extension with more tests

## 📁 Project Structure

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


