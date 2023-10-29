import prompt_toolkit as pt
import re

# Create a validator class for Add/Remove/Edit questions
def add_remove_edit(text):
    is_are = text.lower() in ["add", "remove", "edit"]
    return is_are

add_remove_edit_validator = pt.validation.Validator.from_callable(
    add_remove_edit,
    error_message="Invalid Add/Remove/Edit entry",
    move_cursor_to_end=True
)

# Create a validator class for Yes/No questions
def yes_no(text):
    is_y_n = text.lower() in ["yes", "no", "y", "n"]
    return is_y_n

yes_no_validator = pt.validation.Validator.from_callable(
    yes_no,
    error_message="Invalid Yes/no [Y/n] entry",
    move_cursor_to_end=True
)

# Create a validator class for our software selection
def in_software(text):
    sw = [
        "Julia", "Jupyter", "Pandoc", "Python", "Quarto", "RStudio", "R"
        #, "RMarkdown", "Shiny", "Cuda", "Stata"
    ]
    in_sw = [t in sw for t in text.split()]
    return all(in_sw)

software_validator = pt.validation.Validator.from_callable(
    in_software,
    error_message="This element is not in Tugboat's list of supported software",
    move_cursor_to_end=True
)

# Create a validator class for numeric options
def valid_number(text):
    return text.isdigit()

number_validator = pt.validation.Validator.from_callable(
    valid_number,
    error_message="Invalid option selected",
    move_cursor_to_end=True
)

# Create a validator class for our software version selection
def valid_version(text):
    pattern = r"^[0-9\.\+\-]*$"
    if re.match(pattern, text):
        return True
    return False

software_version_validator = pt.validation.Validator.from_callable(
    valid_version,
    error_message=(
        "Invalid software version (must contain only numbers"
        + ", '.', '+', and '-')"
    ),
    move_cursor_to_end=True
)
