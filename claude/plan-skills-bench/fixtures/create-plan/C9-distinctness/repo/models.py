from dataclasses import dataclass


@dataclass
class Note:
    id: str
    user_id: str
    title: str
    body: str
