from typing import Any, Sequence, TypeVar, Generic

from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args

from pydantic import BaseModel, GetCoreSchemaHandler
from typing import get_origin
T = TypeVar('T')


class FormList(Sequence[T]):
    def __init__(self, v: Sequence[T]):
        self.v = v

    def __getitem__(self, i):
        return self.v[i]

    def __len__(self):
        return len(self.v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(cls)
        args = get_args(source)
        if args:
            sequence_t_schema = handler.generate_schema(Sequence[args[0]])
        else:
            sequence_t_schema = handler.generate_schema(Sequence)
        non_instance_schema = core_schema.no_info_after_validator_function(FormList, sequence_t_schema)
        return core_schema.union_schema([instance_schema, non_instance_schema])

class FormObject(Generic[T]):

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
    
class FormSelect(FormObject[T]):
    pass

class FormFile(FormObject[T]):
    pass

class FormCustom(Generic[T]):

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