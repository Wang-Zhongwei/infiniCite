

class SemanticAPIException(Exception):
    """Base class for API exceptions."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class NoFunctionCallError(Exception):
    pass