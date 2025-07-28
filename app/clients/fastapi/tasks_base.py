import sys
import time
from pathlib import Path
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
sys.path.append(str(Path(__file__).resolve().parents[3]))
from app.clients.fastapi.routers import tasks
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="tasks_base")
app.include_router(tasks.router)
app.include_router(tasks.land_page)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": F"Bad request, request:{request.url}, Error: {exc.detail}"})

