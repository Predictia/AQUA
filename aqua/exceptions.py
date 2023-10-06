
class NotEnoughDataError(Exception):
    def __init__(self, message="Not enough data available"):
        self.message = message
        super().__init__(self.message)
