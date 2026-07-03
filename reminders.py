from datetime import date

def due_soon(tasks, today, days=3):
    today_d = date.fromisoformat(today)
    horizon = (today_d.toordinal() + days)
    out = []
    for t in tasks:
        due = t.get('due')
        if due is None:
            continue
        if t.get('status') == 'done':
            continue
        try:
            due_d = date.fromisoformat(due)
        except ValueError:
            continue
        if today_d.toordinal() <= due_d.toordinal() <= horizon:
            out.append(t)
    return out

def overdue_summary(tasks, today):
    today_d = date.fromisoformat(today)
    lines = []
    for t in tasks:
        due = t.get('due')
        if due is None:
            continue
        if t.get('status') == 'done':
            continue
        try:
            due_d = date.fromisoformat(due)
        except ValueError:
            continue
        if due_d < today_d:
            lines.append(f"[{t.get('id')}] {t.get('title')} (due {due})")
    if not lines:
        return "No overdue tasks."
    return "\n".join(lines)