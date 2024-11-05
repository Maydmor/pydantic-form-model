from pydantic_form_model import FormModel
from typing import Optional

class Address(FormModel):
    zip_code: str

class FormA(FormModel):
    username: str
    password: str
    address: Optional[Address] = None
    numbers: list[int]
    additional_addresses: Optional[list[Address]]
    main_address: Address

print(FormA.get_form_fields())