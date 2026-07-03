def by_status(tasks, status):
    return [t for t in tasks if t.get('status') == status]

def by_project(tasks, project_id):
    return [t for t in tasks if t.get('project_id') == project_id]

def overdue(tasks, today):
    return [t for t in tasks
            if t.get('due') is not None
            and t['due'] < today
            and t.get('status') != 'done']

def search(tasks, keyword):
    kw = keyword.lower()
    return [t for t in tasks
            if kw in t.get('title', '').lower()
            or any(kw in tag.lower() for tag in t.get('tags', []))]

def next_up(tasks, n):
    active = [t for t in tasks if t.get('status') != 'done']
    active.sort(key=lambda t: (t.get('priority', 999), t.get('due') or '9999-99-99'))
    return active[:n]
