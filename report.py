from html import escape

def summary(data):
    projects = {p['id']: p['name'] for p in data.get('projects', [])}
    tasks = data.get('tasks', [])
    counts = {}
    for t in tasks:
        pid = t.get('project_id', '?')
        name = projects.get(pid, pid)
        if name not in counts:
            counts[name] = {'todo': 0, 'in_progress': 0, 'done': 0}
        s = t.get('status', 'todo')
        if s in counts[name]:
            counts[name][s] += 1

    name_width = max((len(n) for n in counts), default=7)
    name_width = max(name_width, 7)
    header = f"{'Project':<{name_width}} | {'todo':>4} | {'in_progress':>11} | {'done':>4} | {'total':>5}"
    sep = '-' * len(header)
    lines = [header, sep]
    totals = {'todo': 0, 'in_progress': 0, 'done': 0}
    for name in sorted(counts):
        c = counts[name]
        total = c['todo'] + c['in_progress'] + c['done']
        lines.append(f"{name:<{name_width}} | {c['todo']:>4} | {c['in_progress']:>11} | {c['done']:>4} | {total:>5}")
        for k in totals:
            totals[k] += c[k]
    grand = sum(totals.values())
    lines.append(sep)
    lines.append(f"{'Total':<{name_width}} | {totals['todo']:>4} | {totals['in_progress']:>11} | {totals['done']:>4} | {grand:>5}")
    return '\n'.join(lines)

def html_report(data):
    projects = {p['id']: p['name'] for p in data.get('projects', [])}
    tasks = data.get('tasks', [])

    grouped = {}
    for t in tasks:
        pid = t.get('project_id', '?')
        name = projects.get(pid, pid)
        grouped.setdefault(name, []).append(t)

    rows = ''
    for i, name in enumerate(sorted(grouped)):
        bg = '#f9f9f9' if i % 2 else '#fff'
        ts = grouped[name]
        todo = sum(1 for t in ts if t.get('status') == 'todo')
        ip = sum(1 for t in ts if t.get('status') == 'in_progress')
        done = sum(1 for t in ts if t.get('status') == 'done')
        rows += f'<tr style="background:{bg}"><td>{escape(name)}</td><td>{todo}</td><td>{ip}</td><td>{done}</td><td>{len(ts)}</td></tr>\n'

    task_rows = ''
    for name in sorted(grouped):
        task_rows += f'<tr><td colspan="4" style="background:#e0e0e0;font-weight:bold">{escape(name)}</td></tr>\n'
        for t in grouped[name]:
            task_rows += (f'<tr><td>{escape(t.get("title",""))}</td>'
                         f'<td>{t.get("priority","")}</td>'
                         f'<td>{escape(t.get("status",""))}</td>'
                         f'<td>{escape(t.get("due","") or "")}</td></tr>\n')

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Taskflow Dashboard</title>
<style>
body {{ font-family: sans-serif; max-width: 900px; margin: 2em auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #4a90d9; color: white; }}
h1 {{ color: #333; }}
</style></head><body>
<h1>Taskflow Dashboard</h1>
<h2>Summary</h2>
<table><tr><th>Project</th><th>Todo</th><th>In Progress</th><th>Done</th><th>Total</th></tr>
{rows}</table>
<h2>All Tasks</h2>
<table><tr><th>Title</th><th>Priority</th><th>Status</th><th>Due</th></tr>
{task_rows}</table>
</body></html>'''
