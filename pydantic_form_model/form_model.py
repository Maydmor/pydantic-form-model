from .base import BaseModel
from .form_fields import *
from typing import get_origin, get_args, Union
from .exceptions import *
from pydantic.fields import FieldInfo


def unpack_union(field_name: str, annotation: type[Union[FormFieldValue]]):
    if len(get_args(annotation)) != 2:
        raise InvalidDefinitionException(f'Unsupported union field "{field_name}": Only Union[T, NoneType] (=Optional[T]) is supported, but type is {annotation}')
    if get_args(annotation)[1] != type(None):
        raise InvalidDefinitionException(f'Unsupported union field "{field_name}": Only Union[T, NoneType] (=Optional[T]) is supported, but type is {annotation}')
    return get_args(annotation)[0]

def is_union(annotation: type):
    return get_origin(annotation) == Union

def is_list(annotation: type):
    return get_origin(annotation) == list

def is_object(annotation: type):
    return issubclass(annotation, FormModel)

def get_list_item_type(annotation: type):
    return get_args(annotation)[0]

def is_number(annotation: type):
    return get_origin(annotation) == int or annotation == int or get_origin(annotation) == float or annotation == float

def is_text(annotation: type):
    return get_origin(annotation) == str or annotation == str

def to_form_field(field_name: str, field: FieldInfo)->FormField:
    annotation = field.annotation
    is_optional = False
    if is_union(annotation):
        annotation = unpack_union(field_name, annotation)
        is_optional = True
    if is_list(annotation):
        list_item_type = get_list_item_type(annotation)
        return ListField(item_definition=to_form_field(field_name, FieldInfo(annotation=list_item_type)))
    elif is_object(annotation):
        return ObjectField(properties=annotation.get_form_fields())
    elif is_number(annotation):
        return NumberField()
    elif is_text(annotation):
        return TextField()
    else:
        raise InvalidDefinitionException(f'Invalid field annotation {field_name}: {annotation}')
    


class FormModel(BaseModel):
    @classmethod
    def get_form_fields(cls)->list[FormField]:
        fields = []
        for field_name, field_info in cls.model_fields.items():
            fields.append(to_form_field(field_name, field_info))
        return fields
    
            
            
