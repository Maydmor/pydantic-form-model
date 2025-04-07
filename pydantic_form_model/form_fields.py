from pydantic import BaseModel, ConfigDict, TypeAdapter
from pydantic_core.core_schema import IntSchema, FloatSchema, StringSchema, ModelSchema, ListSchema, CoreSchemaType
from typing import Optional, TypeVar, Literal, Type, IO, Annotated
from enum import Enum
import base64
from io import BytesIO
from .types import *
from humps import camelize
from typing import Union, ForwardRef, Any

PydanticModelType = TypeVar('PydanticModelType', bound=BaseModel)

T = TypeVar('T')

DataSource = str

class BaseSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(alias_generator=camelize, populate_by_name=True)



# FormValue = FormList|FormObject|FormText|FormNumber|FormSelect|FormBoolean|FormFile
class ValidationRuleName(str, Enum):
    REQUIRED = 'required'
    REQUIRED_IF = 'required_if'
    REQUIRED_UNLESS = 'required_unless'
    SAME_AS = 'same_as' 
    MIN_LENGTH = 'min_length'
    MAX_LENGTH = 'max_length'
    GREATER_THAN = 'greater_than'
    LESS_THAN = 'less_than'

class ValidationRule(BaseSchema):
    name: ValidationRuleName
    error_text: str
    other_field_name: Optional[str] = None
    length: Optional[int] = None
    value: Optional[float] = None
    has_value: Optional[bool] = None
    
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

class RenderCondition(BaseSchema):
    property_path: str
    has_value: Any = None
    render_conditions: list['RenderCondition'] = []

class FormFieldType(str, Enum):
    OBJECT = 'object'
    LIST = 'list'
    NUMBER = 'number'
    TEXT = 'text'
    DATETIME = 'datetime'
    SELECT = 'select'
    FILE = 'file'
    BOOLEAN = 'boolean'


class FormField(BaseSchema):
    model_config: ConfigDict = ConfigDict(alias_generator=lambda name: camelize(name), populate_by_name=True)
    field_type: FormFieldType
    name: str
    hint: Optional[str] = None
    field_index: Optional[int] = 1e7
    default: Optional[Any] = None
    rendered: Optional[bool] = True
    render_conditions: list[RenderCondition] = []
    label: Optional[str] = None
    validation_rules: list[ValidationRule] = []
    item_definition: Optional[Any] = None
    choices: Optional[list[Any]] = None
    data_source: Optional[DataSource] = None
    item_value: Optional[str] = None
    item_text: Optional[str] = None
    item_properties: Optional[list[Any]] = None
    meta: Optional[dict[str, Any]] = {}

class NumberField(FormField):
    field_type: Literal[FormFieldType.NUMBER] = FormFieldType.NUMBER

class TextField(FormField):
    field_type: Literal[FormFieldType.TEXT] = FormFieldType.TEXT

class DateTimeField(FormField):
    field_type: Literal[FormFieldType.DATETIME] = FormFieldType.DATETIME 


class FileField(FormField):
    field_type: Literal[FormFieldType.FILE] = FormFieldType.FILE

class SelectField(FormField):
    field_type: Literal[FormFieldType.SELECT] = FormFieldType.SELECT
    choices: Optional[list[Any]] = None
    data_source: Optional[DataSource] = None
    item_value: Optional[str] = None
    item_text: Optional[str] = None

class BooleanField(FormField):
    field_type: Literal[FormFieldType.BOOLEAN] = FormFieldType.BOOLEAN
    tri_state: Optional[bool] = False

ListField = ForwardRef('ListField')
class CustomField(FormField):
    field_type: str

class ObjectField(FormField):
    field_type: Literal[FormFieldType.OBJECT] = FormFieldType.OBJECT
    item_properties: list[Any]

class ListField(FormField):
    field_type: Literal[FormFieldType.LIST] = FormFieldType.LIST
    item_definition: Any

ListField.model_rebuild()
