from pydantic import BaseModel
from typing import Dict, Optional


class TaskData(BaseModel):
    task_name: str
    task_parameters: Optional[Dict[str, Optional[str]]]
    request_type: str

class ReturnData(BaseModel):
    return_value: Optional[str | dict]
    status_code: int
    validate_resp_val: bool

class FullRequest(BaseModel):
    task_data: TaskData
    return_data: ReturnData
    api_path: str