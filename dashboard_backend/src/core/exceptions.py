class EdgeServerError(Exception):
    """Exception raised for errors in edge server communication."""

    def __init__(self, message: str = "Edge server error"):
        self.message = message
        super().__init__(self.message)
