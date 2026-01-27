# Using pydantic-form-model with FastAPI: Advanced Features and Usage

The `pydantic-form-model` library allows you to define dynamic, structured forms using Pydantic models and serve them as JSON from a FastAPI backend. It supports various field types, including custom types, and provides built-in file handling capabilities. This guide explains how to use `pydantic-form-model` with FastAPI to define, serve, and handle forms, including advanced features like file handling, nested forms, and field properties.

---

## Installation

Install the required dependencies using pip:

```bash
pip install pydantic-form-model
```

---

## Key Features

### 1. Automatic Form Generation
With `pydantic-form-model`, you can define your forms using standard Pydantic classes and built-in Python types. The library automatically generates the form structure based on these definitions, eliminating the need for additional overhead.

For example:

```python
from pydantic_form_model import FormModel, FField
from typing import Optional
from enum import StrEnum

class AvailableCountry(StrEnum):
    austria = 'Austria'
    belgium = 'Belgium'
    canada = 'Canada'

class Address(FormModel):
    country: AvailableCountry = FField(label='Country')
    zip_code: Optional[str] = FField(label='Zip Code', hint='e.g. 12345', default=None)
    street_name: str = FField(label='Street Name', style='width: 75%')
    street_number: Optional[str] = FField(label='Street Number', style='width: 25%')

class UserRegisterForm(FormModel):
    username: str = FField(label='Username', hint='Enter your username')
    password: str = FField(label='Password', hint='Enter your password')
    address: Address = FField(label='Address')
    terms_of_service_agreed: bool = FField(label='I agree to the terms and conditions')
```

The form structure is automatically generated based on the Pydantic model definitions, including validation rules, labels, hints, and more.

---

### 2. Arbitrarily Nested Forms
Forms can be nested arbitrarily, allowing you to create complex form structures. For example:

```python
class PersonalInfo(FormModel):
    first_name: str = FField(label='First Name')
    last_name: str = FField(label='Last Name')

class UserProfile(FormModel):
    personal_info: PersonalInfo = FField(label='Personal Information')
    address: Address = FField(label='Address')
```

The `UserProfile` form will include the nested `PersonalInfo` and `Address` forms, and the JSON representation will reflect this structure.

---

### 3. File Handling
The library provides built-in support for file handling using the `Base64File` type. You can upload files as part of a form and process them using the `save_files` and `load_file_data` methods.

#### Saving Files
The `save_files` method allows you to save uploaded files to a specified directory.

```python
@app.post("/upload-files")
def upload_files(form_data: UserRegisterForm = Depends()):
    form_data.save_files(directory="uploads")
    return {"message": "Files saved successfully"}
```

#### Loading Files
The `load_file_data` method allows you to load file data from a directory and populate the form with the file contents.

```python
@app.get("/load-files")
def load_files():
    form = UserRegisterForm()
    form.load_file_data(directory="uploads")
    return form
```

---

### 4. FormField Properties
Each `FormField` in `pydantic-form-model` has several properties that define its behavior and appearance. These include:

- **`field_type`**: The type of the field (e.g., `text`, `number`, `boolean`, `file`, etc.).
- **`name`**: The name of the field.
- **`label`**: A human-readable label for the field.
- **`hint`**: A short description or hint for the field.
- **`style`**: CSS styling for the field (e.g., width, height).
- **`default`**: The default value for the field.
- **`rendered`**: Whether the field is rendered by default.
- **`validation_rules`**: A list of validation rules for the field (e.g., required, min_length, max_length).
- **`choices`**: A list of predefined options for select fields.
- **`item_properties`**: For object fields, this contains the nested fields.
- **`item_definition`**: For list fields, this defines the structure of the list items.
- **`meta`**: Additional metadata for the field.

Example of a `FormField`:

```json
{
  "name": "username",
  "field_type": "text",
  "label": "Username",
  "hint": "Enter your username",
  "style": null,
  "default": null,
  "rendered": true,
  "validation_rules": [
    {
      "name": "required",
      "error_text": "Username is required."
    }
  ],
  "choices": null,
  "item_properties": null,
  "item_definition": null,
  "meta": {}
}
```

---

## Example: Serving and Handling Forms

Here’s how you can serve and handle forms using `pydantic-form-model` and FastAPI:

```python
from fastapi import FastAPI, Depends
from pydantic_form_model import FormModel, FField
from pydantic_form_model.form_fields import Base64File
from typing import Optional
from enum import StrEnum

app = FastAPI()

class AvailableCountry(StrEnum):
    austria = 'Austria'
    belgium = 'Belgium'
    canada = 'Canada'

class Address(FormModel):
    country: AvailableCountry = FField(label='Country')
    zip_code: Optional[str] = FField(label='Zip Code', hint='e.g. 12345', default=None)
    street_name: str = FField(label='Street Name', style='width: 75%')
    street_number: Optional[str] = FField(label='Street Number', style='width: 25%')

class UserRegisterForm(FormModel):
    username: str = FField(label='Username', hint='Enter your username')
    password: str = FField(label='Password', hint='Enter your password')
    address: Address = FField(label='Address')
    terms_of_service_agreed: bool = FField(label='I agree to the terms and conditions')
    some_file: list[Base64File] = FField(label='Upload Files')

@app.get("/form-definition", response_model=list[FormField])
def get_form_definition():
    form_fields: list[FormField] = UserRegisterForm.get_form_fields()
    return form_fields

@app.post("/submit-form")
def submit_form(form_data: UserRegisterForm = Depends()):
    form_data.save_files(directory="uploads")
    return {"message": f'Form submitted successfully and user {form_data.username} created.'}
```

With `pydantic-form-model`, you can easily define, serve, and handle forms in FastAPI, leveraging its powerful features like automatic form generation, nested forms, file handling, and customizable field properties. This makes it an excellent choice for building dynamic and structured form-based APIs.
