class GenericError(Exception):
    def __init__(self, error_code: int, message: str) -> None:
        self.code = error_code
        self.message = message
        super().__init__(self.message)


class JWTInvalid(GenericError):
    def __init__(self, code: int = 1, message: str = "JWT token is invalid") -> None:
        super().__init__(error_code=code, message=message)


class ServiceUnavailable(GenericError):
    def __init__(self, message: str) -> None:
        super().__init__(error_code=999, message=message)


class EdgeServerError(GenericError):
    def __init__(self, message: str = "Failure when get data in Edge server.") -> None:
        super().__init__(error_code=1, message=message)


class ConnectToEdgeServerError(GenericError):
    def __init__(self, message: str = "Connect to Edge server error.") -> None:
        super().__init__(error_code=2, message=message)


class ErrorReadDataEdgeServer(GenericError):
    def __init__(
        self, message: str = "Some error occurred when read data from edge server."
    ) -> None:
        super().__init__(error_code=3, message=message)
