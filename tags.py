def rename_tag(tasks, old, new):
    for t in tasks:
        tags = t.get('tags')
        if not isinstance(tags, list) or old not in tags or old == new:
            continue
        if new in tags:
            tags = [tag for tag in tags if tag != old]
        else:
            tags = [new if tag == old else tag for tag in tags]
        t['tags'] = tags

def merge_tags(tasks, tag_a, tag_b):
    rename_tag(tasks, tag_b, tag_a)

def tag_counts(tasks):
    counts = {}
    for t in tasks:
        for tag in t.get('tags', []) or []:
            counts[tag] = counts.get(tag, 0) + 1
    return counts