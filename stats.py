from datetime import date, timedelta

def completion_rate(tasks):
    if not tasks:
        return 0.0
    done = sum(1 for t in tasks if t.get('status') == 'done')
    return done / len(tasks)

def by_tag_counts(tasks):
    counts = {}
    for t in tasks:
        for tag in t.get('tags', []):
            counts[tag] = counts.get(tag, 0) + 1
    return counts

def velocity(tasks, done_dates, weeks=4):
    if not done_dates:
        return 0.0
    max_date = max(date.fromisoformat(d) for d in done_dates.values())
    cutoff = max_date - timedelta(weeks=weeks)
    recent = sum(1 for d in done_dates.values()
                 if cutoff <= date.fromisoformat(d) <= max_date)
    return recent / weeks