from pydantic import BaseModel, TypeAdapter
from pydantic_core.core_schema import IntSchema, FloatSchema, StringSchema, ModelSchema, ListSchema, CoreSchemaType
from typing import Optional, TypeVar, Literal, Type, IO, Annotated
from enum import Enum
import base64
from io import BytesIO
from .types import *
class Base64File(BaseModel):
    filename: str
    data: str
    content_type: str
    
    def write(self, file: IO):
        file_data = BytesIO()
        base64.decode(self.data, file_data)
        file.write(file_data)

PydanticModelType = TypeVar('PydanticModelType', bound=BaseModel)

T = TypeVar('T')

DataSource = str



FormValue = FormList|FormObject|FormText|FormNumber|FormSelect|FormBoolean|FormFile
class ValidationRuleName(str, Enum):
    REQUIRED = 'required'
    REQUIRED_IF = 'required_if'
    REQUIRED_UNLESS = 'required_unless'
    SAME_AS = 'same_as' 
    MIN_LENGTH = 'min_length'
    MAX_LENGTH = 'max_length'
    GREATER_THAN = 'greater_than'
    LESS_THAN = 'less_than'

class ValidationRule(BaseModel):
    name: ValidationRuleName
    error_text: str
    
class Required(ValidationRule):
    name: Literal[ValidationRuleName.REQUIRED] = ValidationRuleName.REQUIRED

class RequiredIf(Required):
    name: Literal[ValidationRuleName.REQUIRED_IF] = ValidationRuleName.REQUIRED_IF
    other_field_name: str
    
class RequiredUnless(RequiredIf):
    name: Literal[ValidationRuleName.REQUIRED_UNLESS] = ValidationRuleName.REQUIRED_UNLESS

class SameAs(ValidationRule):
    name: Literal[ValidationRuleName.SAME_AS] = ValidationRuleName.SAME_AS

class MinLength(ValidationRule):
    name: Literal[ValidationRuleName.MIN_LENGTH] = ValidationRuleName.MIN_LENGTH
    length: int

class MaxLength(MinLength):
    name: Literal[ValidationRuleName.MAX_LENGTH] = ValidationRuleName.MAX_LENGTH

class GreaterThan(ValidationRule):
    name: Literal[ValidationRuleName.GREATER_THAN] = ValidationRuleName.GREATER_THAN
    value: float

class LessThan(GreaterThan):
    name: Literal[ValidationRuleName.LESS_THAN] = ValidationRuleName.LESS_THAN

class RenderCondition(BaseModel):
    other_field_name: str
    has_value: bool = True

class FormFieldType(str, Enum):
    OBJECT = 'object'
    LIST = 'list'
    NUMBER = 'number'
    TEXT = 'text'
    SELECT = 'select'
    FILE = 'file'
    BOOLEAN = 'boolean'


class FormField(BaseModel):
    type: FormFieldType
    name: Optional[str] = None
    hint: Optional[str] = None
    default: Optional[FormValue] = None
    rendered: Optional[bool] = True
    render_condition: Optional[RenderCondition] = None
    label: Optional[str] = None
    validation_rules: list[ValidationRule] = []

class NumberField(FormField):
    type: Literal[FormFieldType.NUMBER] = FormFieldType.NUMBER

class TextField(FormField):
    type: Literal[FormFieldType.TEXT] = FormFieldType.TEXT

class FileField(FormField):
    type: Literal[FormFieldType.FILE] = FormFieldType.FILE

class SelectField(FormField):
    type: Literal[FormFieldType.SELECT] = FormFieldType.SELECT
    choices: Optional[list[FormObject|FormText|FormNumber]] = None
    data_source: Optional[DataSource] = None
    item_value: Optional[str] = None
    item_text: Optional[str] = None

class BooleanField(FormField):
    type: Literal[FormFieldType.BOOLEAN] = FormFieldType.BOOLEAN
    tri_state: Optional[bool] = False

class ObjectField(FormField):
    type: Literal[FormFieldType.OBJECT] = FormFieldType.OBJECT
    properties: list[FormField]

class ListField(FormField):
    type: Literal[FormFieldType.LIST] = FormFieldType.LIST
    item_definition: FormField

class CustomField(FormField):
    type: str
