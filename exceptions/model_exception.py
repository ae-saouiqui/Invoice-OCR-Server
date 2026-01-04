



class ModelFailedToLoadException(Exception):
    """
    Raised when a local model fails to initialize or load correctly.

    This exception is typically triggered by missing model files, 
    incompatible formats, or memory constraints during the loading process.
    """
    def __init__(self, message: str = "The local model failed to load."):
        self.message = message
        super().__init__(self.message)