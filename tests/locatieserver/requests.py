from typing import ClassVar, Annotated, Optional
from typing import Literal
from typing import Type

from fastapi import Query

from fastclient import RequestModel

from .models import LookupResponse


class LookupRequest(RequestModel[LookupResponse]):
    method: ClassVar[str] = "GET"
    url: ClassVar[str] = "lookup"
    response_model: ClassVar[Type[LookupResponse]] = LookupResponse

    id: str
    wt: Literal["json"] = "json"
    fl: Annotated[Optional[str], Query()] = None