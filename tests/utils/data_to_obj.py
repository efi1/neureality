from pydantic import BaseModel
from typing import Dict, Optional, Union, Set


class PublicTaskData(BaseModel):
    task_parameters: Optional[Dict[str, Optional[str]]]
    request_type: str

class ReturnData(BaseModel):
    return_value: Optional[Union[str, dict]]
    status_code: int
    validate_resp_val: bool

class PartialRequest(BaseModel):
    task_data: PublicTaskData
    return_data: ReturnData
    api_path: str
    partial_request: Optional[bool] = False

class TaskData(BaseModel):
    task_name: str
    task_parameters: Optional[Dict[str, Optional[str]]]
    request_type: str

class FullRequest(BaseModel):
    task_data: TaskData
    return_data: ReturnData
    api_path: str
    exclude_fields: Optional[Dict[str, set[str]]] = None

    def get_partial_req(self, exclude: Optional[Dict[str, set[str]]] = None) -> PartialRequest:
        return PartialRequest(**self.model_dump(exclude=exclude))




