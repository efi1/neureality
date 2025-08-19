from types import SimpleNamespace
from typing import Any, Union, List, Dict, TypeAlias

# Recursive type alias for "object-like" data
ObjectLikeData: TypeAlias = Union[
    SimpleNamespace,              # namespace object
    Dict[str, "ObjectLikeData"],  # nested dict
    List["ObjectLikeData"],       # nested list
    str, int, float, bool, None   # primitives
]

def data_object(d: Any) -> ObjectLikeData:
    """Recursively convert dict/list into SimpleNamespace-based object."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: data_object(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [data_object(i) for i in d]
    else:
        return d


def object_dump(obj: ObjectLikeData) -> Any:
    """Recursively convert SimpleNamespace back into dict/list."""
    if isinstance(obj, SimpleNamespace):
        return {k: object_dump(v) for k, v in vars(obj).items()}
    elif isinstance(obj, list):
        return [object_dump(item) for item in obj]
    else:
        return obj

