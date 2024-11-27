from pydantic import BaseModel
from .form_fields import *
from .types import *
from typing import get_origin, get_args, Union, Annotated
from .exceptions import *
from pydantic.fields import FieldInfo
import logging
from annotated_types import Gt, Lt, MinLen, MaxLen
import inspect, base64
from os import PathLike

logger = logging.getLogger(__name__)
logger.debug('Test message')


def unpack_annotation(annotation: type):
    while(is_union(annotation) or is_annotated(annotation)):
        annotation = get_args(annotation)[0]
    return annotation
    

def is_union(annotation: type):
    return get_origin(annotation) == Union

def is_list(annotation: type):
    return get_origin(annotation) == list or get_origin == Sequence

def is_dict(annotation: type):
    return annotation == dict

def is_object(annotation: type):
    return inspect.isclass(annotation) and issubclass(annotation, FormModel)

def is_custom(annotation: type):
    return get_origin(annotation) == Custom
 

def is_boolean(annotation: type):
    return annotation == FormBoolean or annotation == bool 

def get_object_type(annotation: type):
    args = get_args(annotation)
    if len(args):
        return args[0]
    return annotation

def get_list_item_type(annotation: type):
    return get_args(annotation)[0]

def is_number(annotation: type):
    return annotation == int or annotation == float or annotation == FormNumber 

def is_select(annotation: type):
    return inspect.isclass(annotation) and issubclass(annotation, Enum) 

def is_file(annotation: type):
    
    return inspect.isclass(annotation) and issubclass(annotation, Base64File) 

def is_literal(annotation: type):
    return get_origin(annotation) == Literal

def is_annotated(annotation: type):
    return get_origin(annotation) == Annotated
def is_text(annotation: type):
    return annotation == FormText

def get_validation_rules(field_name: str, field: FieldInfo):
    validation_rules = []
    for meta in field.metadata:
        if isinstance(meta, Gt):
            validation_rules.append(GreaterThan(value=meta.gt, error_text=f'{field_name} must be greater than {meta.gt}'))
        if isinstance(meta, Lt):
            validation_rules.append(LessThan(value=meta.lt, error_text=f'{field_name} must be less than {meta.lt}'))
        if isinstance(meta, MinLen):
            validation_rules.append(MinLength(length=meta.min_length, error_text=f'Minimum length of {field_name} is {meta.min_length}'))
        if isinstance(meta, MaxLen):
            validation_rules.append(MaxLength(length=meta.max_length, error_text=f'Maximum length of {field_name} is {meta.max_length}'))
    schema_data = field.json_schema_extra
    if schema_data is None:
        schema_data = {}
    if schema_data.get('required_if', None):
        validation_rules.append(RequiredIf(other_field_name=schema_data.get('required_if'), error_text=f'{field_name} is required'))
    if schema_data.get('required_unless', None):
        validation_rules.append(RequiredUnless(other_field_name=schema_data.get('required_unless'), error_text=f'{field_name} is required'))
    if schema_data.get('same_as', None):
        validation_rules.append(SameAs(other_field_name=schema_data.get('same_as'), error_text=f'{field_name} must be same as {schema_data.get("same_as")}'))
    if not is_union(field.annotation):
        validation_rules.append(Required(error_text=f'{field_name} is required.'))
    return validation_rules

def to_form_field(field_name: str, field: FieldInfo)->FormField:
    annotation = field.annotation
    field_schema = field.json_schema_extra
    
    if field_schema is None:
        field_schema = {}
    validation_rules = get_validation_rules(field_schema.get('label', field_name), field)
    field_definition = {
        'name': field_name,
        'validation_rules': validation_rules,
        'default': field.default,
        'meta': field.json_schema_extra
    } | field_schema
    
    logger.debug(f'{field_name} = annotation: {annotation}, schema: {field_definition}, validation rules: {validation_rules}')
    try:
        annotation = unpack_annotation(annotation)            
        if is_custom(annotation):
            return CustomField.model_validate(field_definition)
        elif is_select(annotation):
            return SelectField.model_validate(field_definition)
        elif is_file(annotation):
            return FileField.model_validate(field_definition)
        elif is_list(annotation):
            list_item_type = get_list_item_type(annotation)
            field_definition['item_definition'] = to_form_field(field_name + '_item', FieldInfo(annotation=list_item_type)) 
            return ListField.model_validate(field_definition)
        elif is_object(annotation):
            field_definition['item_properties'] = get_object_type(annotation).get_form_fields() 
            return ObjectField.model_validate(field_definition)
        elif is_dict(annotation):
            logger.warning(f'dict is currently not supported')
        elif is_number(annotation):
            return NumberField.model_validate(field_definition)
        elif is_text(annotation):
            return TextField.model_validate(field_definition)
        elif is_literal(annotation):
            return TextField.model_validate(field_definition | {'rendered': False})
        elif is_boolean(annotation):
            return BooleanField.model_validate(field_definition)
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
    
    def save_file(self, directory: PathLike, file_data: Base64File):
        file_data = Base64FileData.model_validate(file_data)
        with open(f'{directory}/{file_data.filename}', 'wb') as f:
            f.write(base64.b64decode(file_data.data))

    def save_files(self, directory: PathLike):
        for field_name, field_info in self.model_fields.items():
            annotation = field_info.annotation
            annotation = unpack_annotation(annotation)

            if is_list(annotation):
                list_item_type = get_list_item_type(annotation)
                if is_union(list_item_type):
                    list_item_type = unpack_annotation(list_item_type)
                logger.debug(f'list with child item type: {list_item_type}')
                if is_file(list_item_type):
                    for file_data in getattr(self, field_name):
                        self.save_file(directory, file_data)
                elif is_object(list_item_type):
                    get_object_type(annotation).save_files(directory)
            elif is_file(annotation):
                file_data: Base64File = getattr(self, field_name)
                if file_data:
                    self.save_file(directory, file_data)
            elif is_object(annotation):
                get_object_type(annotation).model_validate(getattr(self, field_name)).save_files(directory)


