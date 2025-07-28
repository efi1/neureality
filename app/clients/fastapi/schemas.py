from typing import Optional
from pydantic import BaseModel


class TaskInput(BaseModel):
    """
    defines the http request's input structure
    """
    task_name: str
    task_parameters: Optional[dict] = None

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "task_name": "<task name>",
                "task_parameters": {"param1": "param_val", "param2": "param_val", "n-th_param": "param_val"}
            }
        }


class TaskOutput(BaseModel):
    """
    defines the http request's output structure
    """
    result: str | dict

