# Architecture

## Module interfaces

### models.py
```python
@dataclass
class Project:
    id: str
    name: str

@dataclass
class Task:
    id: str
    project_id: str
    title: str
    priority: int      # 1 = highest
    status: str         # 'todo' | 'in_progress' | 'done'
    due: str | None     # YYYY-MM-DD or None
    tags: list[str]

def validate_task(t: Task) -> list[str]
    # Returns list of error strings; empty = valid
```

### store.py
```python
def load(path: str) -> dict
    # Returns {"projects": [...], "tasks": [...]}
    # Auto-creates empty structure if file missing

def save(data: dict, path: str) -> None
    # Atomic write: tmp file + os.rename
    # Pretty-prints JSON with indent=2
```

### query.py
```python
def by_status(tasks: list[dict], status: str) -> list[dict]
def by_project(tasks: list[dict], project_id: str) -> list[dict]
def overdue(tasks: list[dict], today: str) -> list[dict]
def search(tasks: list[dict], keyword: str) -> list[dict]
def next_up(tasks: list[dict], n: int) -> list[dict]
```
All pure functions. Operate on plain dicts, not dataclass instances.

### report.py
```python
def summary(data: dict) -> str
    # Aligned text table: Project | todo | in_progress | done | total

def html_report(data: dict) -> str
    # Self-contained HTML with inline CSS
```

### importer.py
```python
def from_csv(text: str) -> list[dict]
    # Header-tolerant CSV parsing

def to_csv(tasks: list[dict]) -> str
    # CSV with header row, tags semicolon-separated
```

## Data shapes

### Store file (JSON)
```json
{
  "projects": [
    {"id": "p1", "name": "Website Redesign"}
  ],
  "tasks": [
    {
      "id": "t1",
      "project_id": "p1",
      "title": "Design mockups",
      "priority": 1,
      "status": "todo",
      "due": "2026-07-10",
      "tags": ["design", "ui"]
    }
  ]
}
```

### CSV format
```
id,project_id,title,priority,status,due,tags
t1,p1,Design mockups,1,todo,2026-07-10,design;ui
```
