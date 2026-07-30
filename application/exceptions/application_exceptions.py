
class ApplicationException(Exception):
    pass

class NotFoundApplicationException(ApplicationException):
    pass

class ValidationApplicationException(ApplicationException):
    pass

class ConcurrencyApplicationException(ApplicationException):
    pass
