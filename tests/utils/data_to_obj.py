from pydantic import BaseModel
from typing import Dict, Optional, Union


class TaskData(BaseModel):
    task_name: str
    task_parameters: Optional[Dict[str, Optional[str]]]
    request_type: str

class ReturnData(BaseModel):
    return_value: Optional[Union[str, dict]]
    status_code: int
    validate_resp_val: bool


class FullRequest(BaseModel):
    task_data: TaskData
    return_data: ReturnData
    api_path: str
    partial_request: Optional[bool] = False


class TaskDataPartial(BaseModel):
    task_parameters: Optional[Dict[str, Optional[str]]]
    request_type: str


class PartialRequest(BaseModel):
    task_data: TaskDataPartial
    return_data: ReturnData
    api_path: str
    partial_request: Optional[bool] = False