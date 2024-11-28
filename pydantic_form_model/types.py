from typing import Any, Sequence, TypeVar, Generic

from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args
import base64
from pydantic import BaseModel, GetCoreSchemaHandler, field_serializer, FieldSerializationInfo
from typing import get_origin, Optional
from os import PathLike
from io import BytesIO
T = TypeVar('T')


class File(Generic[T]):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        origin = get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            origin = source_type
            item_tp = Any
        else:
            item_tp = get_args(source_type)[0]
        # both calling handler(...) and handler.generate_schema(...)
        # would work, but prefer the latter for conceptual and consistency reasons
        item_schema = handler.generate_schema(item_tp)
        return item_schema
    
    def save(self, path: PathLike):
        raise Exception('Not implemented')

class Base64FileData(BaseModel):
    data: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    @field_serializer('data')
    def serialize_base64_data(self, base_64_data: str, info: FieldSerializationInfo):
        if not info.mode_is_json():
            if self.path:
                with open(self.path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
        return None
    

class Base64File(Base64FileData, File[Base64FileData]):
    pass

class Custom(Generic[T]):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        origin = get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            origin = source_type
            item_tp = Any
        else:
            item_tp = get_args(source_type)[0]
        # both calling handler(...) and handler.generate_schema(...)
        # would work, but prefer the latter for conceptual and consistency reasons
        item_schema = handler.generate_schema(item_tp)
        return item_schema
    

FormNumber = int|float
FormText = str
FormBoolean = bool