import csv
import io

def from_csv(text):
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    first = rows[0]
    if any(cell.strip().lower() in ('title', 'id') for cell in first):
        rows = rows[1:]
    result = []
    for row in rows:
        while len(row) < 7:
            row.append('')
        tags_raw = row[6].strip()
        tags = [t.strip() for t in tags_raw.split(';') if t.strip()] if tags_raw else []
        due = row[5].strip() or None
        result.append({
            'id': row[0].strip(),
            'project_id': row[1].strip(),
            'title': row[2].strip(),
            'priority': int(row[3].strip()) if row[3].strip() else 0,
            'status': row[4].strip(),
            'due': due,
            'tags': tags,
        })
    return result

def to_csv(tasks):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'project_id', 'title', 'priority', 'status', 'due', 'tags'])
    for t in tasks:
        tags = t.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        writer.writerow([
            t.get('id', ''),
            t.get('project_id', ''),
            t.get('title', ''),
            t.get('priority', 0),
            t.get('status', ''),
            t.get('due', '') or '',
            ';'.join(tags),
        ])
    return output.getvalue()
