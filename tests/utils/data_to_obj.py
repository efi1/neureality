from types import SimpleNamespace
from typing import Any, Union

ObjectLikeData = Union[list[SimpleNamespace | list[
    Any] | str | int | float | bool | None] | SimpleNamespace | dict:]

def data_object(d: dict) -> ObjectLikeData:
    """Recursively converts a nested dictionary or list into a SimpleNamespace-based object."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: data_object(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [data_object(i) for i in d]
    else:
        return d


def object_dump(obj: Any) -> Any:
    """Recursively converts a SimpleNamespace-based object back into a dictionary or list."""
    if isinstance(obj, SimpleNamespace):
        return {k: object_dump(v) for k, v in vars(obj).items()}
    elif isinstance(obj, list):
        return [object_dump(item) for item in obj]
    else:
        return obj

