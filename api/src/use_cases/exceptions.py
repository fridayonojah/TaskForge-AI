class EmptyQueryError(Exception):
    pass

class PlanningFailedError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class JobNotFoundError(Exception):
    pass

class RateLimitExceededError(Exception):
    pass

class ServiceUnavailableError(Exception):
    pass
