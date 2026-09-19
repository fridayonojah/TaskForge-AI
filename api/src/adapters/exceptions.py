class ExternalServiceError(Exception):
    pass

class FlightApiError(ExternalServiceError):
    pass

class HotelApiError(ExternalServiceError):
    pass

class LLMError(ExternalServiceError):
    pass

class DatabaseError(Exception):
    pass

class CacheError(Exception):
    pass
