import types
import typing
import annotated_types
import typing_extensions
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, TypeAdapter, Field, types
from pydantic_core import PydanticUndefined
from pydantic.config import JsonDict
from pydantic.fields import _Unset, _EmptyKwargs, FieldInfo, Deprecated
from pydantic_core.core_schema import IntSchema, FloatSchema, StringSchema, ModelSchema, ListSchema, CoreSchemaType
from typing import Optional, TypeVar, Literal, Type, IO, Annotated, Unpack
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
    style: Optional[str] = None
    field_index: Optional[int] = int(1e7)
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


def FField(  # noqa: C901
    default: Any = PydanticUndefined,
    default_factory: typing.Callable[[], Any] | None = _Unset,
    alias: str | None = _Unset,
    field_type: FormFieldType | None = _Unset,
    hint: Optional[str] = _Unset,
    style: Optional[str] = _Unset,
    field_index: Optional[int] = int(1e7),
    rendered: Optional[bool] = True,
    render_conditions: list[RenderCondition] = [],
    label: Optional[str] = _Unset,
    validation_rules: Optional[list[ValidationRule]] = [],
    choices: Optional[list[Any]] = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: typing_extensions.Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | types.Discriminator | None = _Unset,
    deprecated: Deprecated | str | bool | None = _Unset,
    json_schema_extra: JsonDict | typing.Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    *args,
    **kwargs
) -> Any:
    """Usage docs: https://docs.pydantic.dev/2.9/concepts/fields
    (Extended with parameters for pydantic_form_model fields)
    Create a field for objects that can be configured.

    Used to provide extra information about a field, either for the model schema or complex validation. Some arguments
    apply only to number fields (`int`, `float`, `Decimal`) and some apply only to `str`.

    Note:
        - Any `_Unset` objects will be replaced by the corresponding value defined in the `_DefaultValues` dictionary. If a key for the `_Unset` object is not found in the `_DefaultValues` dictionary, it will default to `None`

    Args:
        default: Default value if the field is not set.
        default_factory: A callable to generate the default value, such as :func:`~datetime.utcnow`.
        alias: The name to use for the attribute when validating or serializing by alias.
            This is often used for things like converting between snake and camel case.
        field_type: The field type for this field (use this to overwrite the inferred field type from the type annotation),
        hint: Hint for the field (usually a short description),
        style: CSS stylings to store for this field,
        field_index: Index property (can be used to sort fields),
        rendered: Wether this field is rendered by default or not,
        render_conditions: List of render conditions,
        label: Text label for this fields,
        validation_rules: A list of additional validation rules for this field,
        choices: Choices for this field (can be used to store possible selections),
        alias_priority: Priority of the alias. This affects whether an alias generator is used.
        validation_alias: Like `alias`, but only affects validation, not serialization.
        serialization_alias: Like `alias`, but only affects serialization, not validation.
        title: Human-readable title.
        field_title_generator: A callable that takes a field name and returns title for it.
        description: Human-readable description.
        examples: Example values for this field.
        exclude: Whether to exclude the field from the model serialization.
        discriminator: Field name or Discriminator for discriminating the type in a tagged union.
        deprecated: A deprecation message, an instance of `warnings.deprecated` or the `typing_extensions.deprecated` backport,
            or a boolean. If `True`, a default deprecation message will be emitted when accessing the field.
        json_schema_extra: A dict or callable to provide extra JSON schema properties.
        frozen: Whether the field is frozen. If true, attempts to change the value on an instance will raise an error.
        validate_default: If `True`, apply validation to the default value every time you create an instance.
            Otherwise, for performance reasons, the default value of the field is trusted and not validated.
        repr: A boolean indicating whether to include the field in the `__repr__` output.
        init: Whether the field should be included in the constructor of the dataclass.
            (Only applies to dataclasses.)
        init_var: Whether the field should _only_ be included in the constructor of the dataclass.
            (Only applies to dataclasses.)
        kw_only: Whether the field should be a keyword-only argument in the constructor of the dataclass.
            (Only applies to dataclasses.)
        coerce_numbers_to_str: Whether to enable coercion of any `Number` type to `str` (not applicable in `strict` mode).
        strict: If `True`, strict validation is applied to the field.
            See [Strict Mode](../concepts/strict_mode.md) for details.
        gt: Greater than. If set, value must be greater than this. Only applicable to numbers.
        ge: Greater than or equal. If set, value must be greater than or equal to this. Only applicable to numbers.
        lt: Less than. If set, value must be less than this. Only applicable to numbers.
        le: Less than or equal. If set, value must be less than or equal to this. Only applicable to numbers.
        multiple_of: Value must be a multiple of this. Only applicable to numbers.
        min_length: Minimum length for iterables.
        max_length: Maximum length for iterables.
        pattern: Pattern for strings (a regular expression).
        allow_inf_nan: Allow `inf`, `-inf`, `nan`. Only applicable to numbers.
        max_digits: Maximum number of allow digits for strings.
        decimal_places: Maximum number of decimal places allowed for numbers.
        union_mode: The strategy to apply when validating a union. Can be `smart` (the default), or `left_to_right`.
            See [Union Mode](../concepts/unions.md#union-modes) for details.
        fail_fast: If `True`, validation will stop on the first error. If `False`, all validation errors will be collected.
            This option can be applied only to iterable types (list, tuple, set, and frozenset).

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo]. The return annotation is `Any` so `Field` can be used on
            type-annotated fields without causing a type error.
    """
    return Field(
        default = default,
        default_factory = default_factory,
        alias = alias,
        field_type = field_type,
        hint = hint,
        style = style,
        field_index = field_index,
        rendered = rendered,
        render_conditions = render_conditions,
        label = label,
        validation_rules = validation_rules,
        choices = choices,
        alias_priority = alias_priority,
        validation_alias = validation_alias,
        serialization_alias = serialization_alias,
        title = title,
        field_title_generator = field_title_generator,
        description = description,
        examples = examples,
        exclude = exclude,
        discriminator = discriminator,
        deprecated = deprecated,
        json_schema_extra = json_schema_extra,
        frozen = frozen,
        validate_default = validate_default,
        repr = repr,
        init = init,
        init_var = init_var,
        kw_only = kw_only,
        pattern = pattern,
        strict = strict,
        coerce_numbers_to_str = coerce_numbers_to_str,
        gt = gt,
        ge = ge,
        lt = lt,
        le = le,
        multiple_of = multiple_of,
        allow_inf_nan = allow_inf_nan,
        max_digits = max_digits,
        decimal_places = decimal_places,
        min_length = min_length,
        max_length = max_length,
        union_mode = union_mode,
        fail_fast = fail_fast,
        *args, **kwargs)