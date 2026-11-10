import re

if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", "{{ cookiecutter.component_name }}") is None:
    raise ValueError("Unacceptable component name: use an identifier (letters, digits, underscore)")
