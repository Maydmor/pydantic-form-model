from .base import BaseModel
from .form_fields import *
from .types import *
from typing import get_origin, get_args, Union
from .exceptions import *
from pydantic.fields import FieldInfo
import logging

logger = logging.getLogger(__name__)

def unpack_union(annotation: type[Union[FormValue]]):
    if len(get_args(annotation)) != 2:
        raise InvalidDefinitionException(f'Only Union[T, NoneType] (=Optional[T]) is supported, but type is {annotation}')
    if get_args(annotation)[1] != type(None):
        raise InvalidDefinitionException(f'Only Union[T, NoneType] (=Optional[T]) is supported, but type is {annotation}')
    return get_args(annotation)[0]

def is_union(annotation: type):
    return get_origin(annotation) == Union

def is_list(annotation: type):
    print(f'is list {annotation}: {get_origin(annotation)}')
    return get_origin(annotation) == FormList or get_origin(annotation) == list or get_origin == Sequence

def is_object(annotation: type):
    return get_origin(annotation) == FormObject or get_origin(annotation) == BaseModel or issubclass(annotation, BaseModel)

def is_custom(annotation: type):
    return get_origin(annotation) == FormCustom

def get_object_type(annotation: type):
    print(f'object args {get_args(annotation)}')
    args = get_args(annotation)
    if len(args):
        return args[0]
    return annotation

def get_list_item_type(annotation: type):
    return get_args(annotation)[0]

def is_number(annotation: type):
    return annotation == int or annotation == float or annotation == FormNumber 

def is_select(annotation: type):
    return get_origin(annotation) == FormSelect

def is_file(annotation: type):
    return annotation == FormFile

def is_text(annotation: type):
    return annotation == FormText

def to_form_field(field_name: str, field: FieldInfo)->FormField:
    annotation = field.annotation
    is_optional = False
    field_schema = field.json_schema_extra
    if field_schema is None:
        field_schema = {}
    print(f'field_name: {field.annotation}')
    validation_rules = []
    try:
        if is_union(annotation):
            annotation = unpack_union(annotation)
        else:
            validation_rules.append(Required(error_text=field_schema.get('required_error_message', f'{field_schema.get('label', field_name)} is required.')))
        field_definition = {
            'name': field_name,
            'validation_rules': validation_rules
        } | field_schema
        if is_select(annotation):
            return SelectField.model_validate(field_definition)
        elif is_file(annotation):
            return FileField.model_validate(field_definition)
        elif is_custom(annotation):
            return CustomField.model_validate(field_definition)
        elif is_list(annotation):
            list_item_type = get_list_item_type(annotation)
            field_definition['item_definition'] = to_form_field(field_name + '_item', FieldInfo(annotation=list_item_type)) 
            return ListField.model_validate(field_definition)
        elif is_object(annotation):
            field_definition['properties'] = get_object_type(annotation).get_form_fields() 
            return ObjectField.model_validate(field_definition)
        elif is_number(annotation):
            return NumberField.model_validate(field_definition)
        elif is_text(annotation):
            return TextField.model_validate(field_definition)
        else:
            raise InvalidDefinitionException(f'Invalid field annotation {field_name}: {annotation}')
    except InvalidDefinitionException as e:
        e.message = f'Invalid field {field_name}: {e.message}'
        raise e


class FormModel(BaseModel):
    @classmethod
    def get_form_fields(cls)->list[FormField]:
        fields = []
        for field_name, field_info in cls.model_fields.items():
            fields.append(to_form_field(field_name, field_info))
        return fields
    
            
            
