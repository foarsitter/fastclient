"""Fastclient."""


from collections import defaultdict
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar

import fastapi
import httpx
from fastapi import params
from fastapi.encoders import jsonable_encoder
from httpx import Request
from httpx._client import BaseClient
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.fields import FieldInfo


ResponseType = TypeVar("ResponseType", bound=BaseModel)


class RequestModel(BaseModel, Generic[ResponseType]):
    model_config = ConfigDict(populate_by_name=True)
    url: ClassVar[str]
    method: ClassVar[str]

    response_model: ClassVar[Type[ResponseType]]  # type: ignore[misc]

    body: Optional[ResponseType] = None

    def as_request(self, client: BaseClient) -> Request:
        request_args: Dict[Type[FieldInfo], Dict[str, Any]] = defaultdict(dict)

        for k, v in self.__annotations__.items():
            if hasattr(v, "__metadata__"):
                annotated_property = v.__metadata__[0]
            else:
                annotated_property = fastapi.Query()

            request_args[type(annotated_property)][k] = getattr(self, k)

        body = jsonable_encoder(self.body) if self.body else None

        headers = request_args[params.Header]
        headers["accept"] = "application/json"

        r = Request(
            method=self.method,
            url=client._merge_url(self.url.format(**request_args[params.Path])),
            params=request_args[params.Query],
            headers=headers,
            cookies=request_args[params.Cookie],
            data=request_args[params.Body],
            files=request_args[params.File],
            json=body,
        )

        return r

    def send(self, client: httpx.Client) -> ResponseType:
        r = self.as_request(client)
        response = client.send(r)
        response.raise_for_status()
        return self.response_model.model_validate(response.json())

    async def asend(self, client: httpx.AsyncClient) -> ResponseType:
        r = self.as_request(client)
        response = await client.send(r)
        return self.response_model.model_validate(response.json())
