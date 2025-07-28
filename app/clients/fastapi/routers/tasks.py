from fastapi import APIRouter, Request, HTTPException
from app.clients.fastapi.schemas import TaskInput, TaskOutput

router = APIRouter(prefix="/api/task")
land_page = APIRouter()


@land_page.get("/")
def welcome():
    """returns friendly welcome message"""
    return {"message": F"Welcome to reverse and restore handler"}


@router.post("/reverse", response_model=TaskOutput)
async def reverse(task_data: TaskInput, request: Request) -> TaskOutput:
    """
    reverse a given parts of a string; e.g: "The cute boy" -> "boy cute The"
    :param request: FastAPI Request object to save the state of this call.
    :param task_data: a given string.
    :return: reversed parts of the string
    """
    params = task_data.task_parameters
    string = params.get('given string')
    if string:
        s = ' '.join(reversed(string.split()))
    else:
        raise HTTPException(status_code=404, detail=F"no string was given")
    await save_response(request, s)
    output = TaskOutput(result=s)
    return output.model_dump()


@router.get("/restore", response_model=TaskOutput)
async def restore(request: Request) -> TaskOutput:
    """
    restore the last result of the reverse api call.
    :param request: FastAPI Request object to save the state of this call.
    :return: reversed parts of the string
    """
    last_response = await get_last_response(request)
    output = TaskOutput(result=last_response)
    return output.model_dump()


@router.post("/save_response")
async def save_response(request: Request, data: str):
    request.app.state.last_response = data
    return "data saved for restore"


# GET endpoint to retrieve the saved result
@router.get("/last_response")
async def get_last_response(request: Request):
    return getattr(request.app.state, "last_response", "No data yet")
