from dataclasses import dataclass, field
import re

@dataclass
class Project:
    id: str
    name: str

@dataclass
class Task:
    id: str
    project_id: str
    title: str
    priority: int
    status: str
    due: str | None = None
    tags: list = field(default_factory=list)

def validate_task(t) -> list[str]:
    errors = []
    if not isinstance(t.get('id', ''), str) or not t.get('id', '').strip():
        errors.append('id must be a non-empty string')
    if not isinstance(t.get('title', ''), str) or not t.get('title', '').strip():
        errors.append('title must be a non-empty string')
    if not isinstance(t.get('priority', 0), int) or t.get('priority', 0) < 1:
        errors.append('priority must be a positive integer')
    if t.get('status') not in ('todo', 'in_progress', 'done'):
        errors.append("status must be one of 'todo', 'in_progress', 'done'")
    due = t.get('due')
    if due is not None:
        if not isinstance(due, str) or not re.match(r'^\d{4}-\d{2}-\d{2}$', due):
            errors.append('due must be in YYYY-MM-DD format')
    tags = t.get('tags', [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        errors.append('tags must be a list of strings')
    return errors
