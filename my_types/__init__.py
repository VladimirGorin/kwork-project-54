from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: Optional[str] = None
    inviter_id: Optional[int] = 0
    current_refers: Optional[int] = 0
    blocked: Optional[bool] = False
    is_admin: Optional[bool] = False


@dataclass
class Job:
    job_id: int
    job_type: str
    start: str
    state: str
    message: Optional[str] = None
    photo: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[str] = None
    users: Optional[list] = None
    message_id: Optional[int] = None
