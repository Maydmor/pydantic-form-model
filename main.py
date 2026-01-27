from pydantic_form_model import FormModel
from pydantic_form_model.form_fields import *
from typing import Optional
from enum import StrEnum
import logging, pprint

# logging.basicConfig(level=logging.DEBUG)


class AvailableCountry(StrEnum):
    austria = 'Austria'
    belgium = 'Belgium'
    canada = 'Canada'


class UserCredentials(FormModel):
    username: str = FField(label='Username', hint='Username')
    password: str = FField(label='Password', hint='Password')

class RegisterCredentials(UserCredentials):
    password_repeat: str = FField(label='Repeat password', hint='Repeat your provided password')

class Address(FormModel):
    country: AvailableCountry = FField(label='Country')
    zip_code: Optional[str] = FField(label='Zip Code', hint='e.g. 12345', default=None)
    street_name: str = FField(label='Street Name', style='width: 75%')
    street_number: Optional[str] = FField(label='Street Number', style='width: 25%')

class UserLoginForm(FormModel):
    credentials: UserCredentials = FField(label='Login')
    terms_of_service_agreed: bool = FField(label='I agree to the terms and conditions')

class UserRegisterForm(FormModel):
    credentials: RegisterCredentials = FField(label='Register')
    address: Address = FField(label='Address')
    terms_of_service_agreed: bool = FField(label='I agree to the terms and conditions')
# UserRegisterForm.get_form_fields()
form_data = {form_field.name: form_field.model_dump() for form_field in UserLoginForm.get_form_fields()}
pretty_printer = pprint.PrettyPrinter(depth=100)
pretty_printer.pprint(form_data)
# pprint.PrettyPrinter(form_data)
