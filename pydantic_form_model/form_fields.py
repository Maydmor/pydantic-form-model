from pydantic import BaseModel
from typing import Optional, TypeVar, Literal

PydanticModelType = TypeVar('PydanticModelType', bound=BaseModel)
FormFieldValue = PydanticModelType|str|int|float

class FormField(BaseModel):
    type: Literal['object','list','number','text']
    name: Optional[str] = None
    hint: Optional[str] = None
    default: Optional[FormFieldValue] = None
    required: Optional[bool] = None
    rendered: Optional[bool] = True
    label: Optional[str] = None





class NumberField(FormField):
    type: Literal['number'] = 'number'

class TextField(FormField):
    type: Literal['text'] = 'text'

class ObjectField(FormField):
    type: Literal['object'] = 'object'
    properties: list[FormField]

class ListField(FormField):
    type: Literal['list'] = 'list'
    item_definition: FormField

