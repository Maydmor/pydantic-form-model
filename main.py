from pydantic_form_model import FormModel
from pydantic_form_model.form_fields import *
from pydantic import Field, EmailStr
from typing import Optional

class Address(FormModel):
    zip_code: str

class FormA(FormModel):
    username: str = Field(label='Username or E-Mail', hint="Yours", min_length=10)
    password: FormText
    address: Optional[FormObject[Address]] = None
    numbers: FormList[int]
    additional_addresses: FormList[Address]
    main_address: FormObject[Address]
    primary_address: FormSelect[Address]
    custom_address: FormCustom[Address] = Field(type='address')
for field in FormA.get_form_fields():
    print(field)
    print()