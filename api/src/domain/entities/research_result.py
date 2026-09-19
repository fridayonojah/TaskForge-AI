from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId

@dataclass
class ResearchResult:
    industry: str
    summary: str
    trends: str
    key_players: str
    thread_id: ThreadId
