import re


CODE_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")


def normalize_code(value: str) -> str:
    """
    Normalize user input into a SKU-safe code.

    Examples:
        "dark blue" -> "DARK-BLUE"
        "Dark Blue" -> "DARK-BLUE"
        " dark_blue " -> "DARK-BLUE"
        "red/white" -> "RED-WHITE"
    """
    value = value.strip().upper()

    # Convert common separators/spaces to "-"
    value = re.sub(r"[\s_/]+", "-", value)

    # Remove anything that isn't alphanumeric or "-"
    value = re.sub(r"[^A-Z0-9-]", "", value)

    # Collapse repeated separators
    value = re.sub(r"-+", "-", value)

    # Remove leading/trailing separators
    value = value.strip("-")

    return value


def validate_code(value: str, max_length: int = 20) -> tuple[bool, str]:
    """
    Validate a normalized SKU component.
    """
    if not value:
        return False, "The code cannot be empty."

    if len(value) > max_length:
        return False, f"The code cannot exceed {max_length} characters."

    if not CODE_PATTERN.fullmatch(value):
        return False, "Only A-Z, 0-9 and '-' are allowed."

    return True, ""


def normalize_and_validate(value: str) -> tuple[str | None, str | None]:
    """
    Normalize and validate a value.

    Returns:
        (normalized_value, None) on success
        (None, error_message) on failure
    """
    normalized = normalize_code(value)

    valid, error = validate_code(normalized)

    if not valid:
        return None, error

    return normalized, None
