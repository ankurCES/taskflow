#!/usr/bin/env python3
import argparse
import sys
import uuid
import store
import query
import report
import importer
import reminders
import stats
import archive as archive_mod
import tags
import validate

DEFAULT_STORE = 'taskflow.json'

def cmd_add(args):
    data = store.load(args.store)
    pid = args.project
    if pid and not any(p['id'] == pid for p in data['projects']):
        data['projects'].append({'id': pid, 'name': pid})
    task = {
        'id': str(uuid.uuid4())[:8],
        'project_id': pid or '',
        'title': args.title,
        'priority': args.priority,
        'status': 'todo',
        'due': args.due,
        'tags': [t.strip() for t in args.tags.split(',')] if args.tags else [],
    }
    data['tasks'].append(task)
    store.save(data, args.store)
    print(f"Added task {task['id']}: {task['title']}")

def cmd_list(args):
    data = store.load(args.store)
    tasks = data['tasks']
    if args.status:
        tasks = query.by_status(tasks, args.status)
    if args.project:
        tasks = query.by_project(tasks, args.project)
    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        due = t.get('due') or ''
        tags = ','.join(t.get('tags', []))
        print(f"[{t['id']}] {t['title']} (p{t['priority']}) [{t['status']}] due:{due} tags:{tags}")

def cmd_done(args):
    data = store.load(args.store)
    for t in data['tasks']:
        if t['id'] == args.task_id:
            t['status'] = 'done'
            store.save(data, args.store)
            print(f"Marked {args.task_id} as done.")
            return
    print(f"Task {args.task_id} not found.")
    sys.exit(1)

def cmd_report(args):
    data = store.load(args.store)
    print(report.summary(data))

def cmd_export(args):
    data = store.load(args.store)
    if args.html:
        html = report.html_report(data)
        with open('dashboard.html', 'w') as f:
            f.write(html)
        print("Wrote dashboard.html")
    else:
        print(importer.to_csv(data['tasks']), end='')

def cmd_import(args):
    with open(args.file, 'r') as f:
        text = f.read()
    tasks = importer.from_csv(text)
    data = store.load(args.store)
    data['tasks'].extend(tasks)
    store.save(data, args.store)
    print(f"Imported {len(tasks)} tasks.")

def cmd_remind(args):
    from datetime import date
    data = store.load(args.store)
    today = args.today or date.today().isoformat()
    soon = reminders.due_soon(data['tasks'], today, days=args.days)
    if soon:
        print(f"Tasks due within {args.days} days:")
        for t in soon:
            print(f"  [{t['id']}] {t['title']} (due {t['due']})")
    else:
        print("No upcoming tasks.")
    summary = reminders.overdue_summary(data['tasks'], today)
    print(summary)

def cmd_stats(args):
    data = store.load(args.store)
    rate = stats.completion_rate(data['tasks'])
    print(f"Completion rate: {rate:.0%}")
    tc = stats.by_tag_counts(data['tasks'])
    if tc:
        print("Tag counts:")
        for tag, count in sorted(tc.items()):
            print(f"  {tag}: {count}")

def cmd_archive(args):
    data = store.load(args.store)
    archive_mod.archive_done(data, args.archive_path)
    store.save(data, args.store)
    print(f"Archived done tasks to {args.archive_path}")

def cmd_restore(args):
    data = store.load(args.store)
    archive_mod.restore(data, args.archive_path, args.task_id)
    store.save(data, args.store)
    print(f"Restored task {args.task_id}")

def cmd_tags(args):
    data = store.load(args.store)
    if args.tags_action == 'rename':
        tags.rename_tag(data['tasks'], args.old, args.new)
        store.save(data, args.store)
        print(f"Renamed tag '{args.old}' → '{args.new}'")
    elif args.tags_action == 'merge':
        tags.merge_tags(data['tasks'], args.into, args.from_tag)
        store.save(data, args.store)
        print(f"Merged tag '{args.from_tag}' into '{args.into}'")
    elif args.tags_action == 'counts':
        tc = tags.tag_counts(data['tasks'])
        for tag, count in sorted(tc.items()):
            print(f"{tag}: {count}")

def cmd_lint(args):
    data = store.load(args.store)
    errors = validate.lint(data)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("All clean.")

def main():
    parser = argparse.ArgumentParser(prog='taskflow', description='Project/task manager')
    parser.add_argument('--store', default=DEFAULT_STORE, help='JSON store path')
    sub = parser.add_subparsers(dest='command')

    p_add = sub.add_parser('add')
    p_add.add_argument('--project', default='')
    p_add.add_argument('--title', required=True)
    p_add.add_argument('--priority', type=int, default=3)
    p_add.add_argument('--due', default=None)
    p_add.add_argument('--tags', default='')

    p_list = sub.add_parser('list')
    p_list.add_argument('--status', default=None)
    p_list.add_argument('--project', default=None)

    p_done = sub.add_parser('done')
    p_done.add_argument('task_id')

    sub.add_parser('report')

    p_export = sub.add_parser('export')
    p_export.add_argument('--html', action='store_true')

    p_import = sub.add_parser('import')
    p_import.add_argument('file')

    p_remind = sub.add_parser('remind')
    p_remind.add_argument('--today', default=None)
    p_remind.add_argument('--days', type=int, default=3)

    sub.add_parser('stats')

    p_archive = sub.add_parser('archive')
    p_archive.add_argument('--archive-path', default='archive.json')

    p_restore = sub.add_parser('restore')
    p_restore.add_argument('task_id')
    p_restore.add_argument('--archive-path', default='archive.json')

    p_tags = sub.add_parser('tags')
    tags_sub = p_tags.add_subparsers(dest='tags_action')
    p_tags_rename = tags_sub.add_parser('rename')
    p_tags_rename.add_argument('old')
    p_tags_rename.add_argument('new')
    p_tags_merge = tags_sub.add_parser('merge')
    p_tags_merge.add_argument('into')
    p_tags_merge.add_argument('from_tag')
    tags_sub.add_parser('counts')

    sub.add_parser('lint')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        'add': cmd_add, 'list': cmd_list, 'done': cmd_done,
        'report': cmd_report, 'export': cmd_export, 'import': cmd_import,
        'remind': cmd_remind, 'stats': cmd_stats, 'archive': cmd_archive,
        'restore': cmd_restore, 'tags': cmd_tags, 'lint': cmd_lint,
    }
    cmds[args.command](args)

if __name__ == '__main__':
    main()
