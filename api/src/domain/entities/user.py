from dataclasses import dataclass, field
from datetime import datetime
from domain.value_objects.user_id import UserId

@dataclass
class User:
    id: UserId
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
