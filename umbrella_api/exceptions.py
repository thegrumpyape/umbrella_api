import json


class UmbrellaAPIError(Exception):
    def __init__(self, status_code=None, text=None, url=None):
        self.status_code = status_code
        self.text = text
        self.url = url

    def __str__(self):
        if self.text:
            return 'HTTP {0}: "{1}"\n{2}'.format(self.status_code, self.text, self.url)
        else:
            return "HTTP {0}: {1}".format(self.status_code, self.url)


class InputValidationError(Exception):
    message = "Invalid input"

    def __init__(self, message=None, errors=None):
        super().__init__(message or self.message)
        self.errors = errors or {}


def raise_on_error(r):
    if r.status_code >= 400:
        error = ""
        if r.text:
            try:
                response = json.loads(r.text)
                if "message" in response:
                    error = response["message"]
                else:
                    error = r.text
            except ValueError:
                error = r.text
        raise UmbrellaAPIError(r.status_code, error, r.url)
    else:
        return True


def validate_input(input_data, expected_type: type):
    if not input_data:
        raise InputValidationError("Input data is empty")
    elif not isinstance(input_data, expected_type):
        raise InputValidationError(
            f"Input data is not of expected type {expected_type.__name__}"
        )
    else:
        return True
