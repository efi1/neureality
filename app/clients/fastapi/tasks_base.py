# import uvicorn # - for debugging purposes only.
import sys
import time
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse
from app.clients.fastapi.routers import tasks
from starlette.exceptions import HTTPException as StarletteHTTPException


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("fastapi")

app = FastAPI(title="tasks_base")
app.include_router(tasks.router)
app.include_router(tasks.land_page)
app.include_router(tasks.health_check)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Completed in {process_time:.2f}s: {request.method} {request.url.path} → {response.status_code}")
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": F"Bad request, request:{request.url}, Error: {exc.detail}"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # safely extract from exc.args
    error_list = exc.args[0] if exc.args else []

    # find missing fields
    missing_fields = [
        error["loc"][-1] for error in error_list
        if error.get("type") == "missing"
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "result": F"Required field is missing: {missing_fields}, Error: {exc.errors()}"  # or customize further if needed
        }
    )



# if __name__ == '__main__':
#     if __name__ == '__main__':
#         uvicorn.run("tasks_base:app", reload=True)
