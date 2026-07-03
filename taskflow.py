#!/usr/bin/env python3
import argparse
import sys
import uuid
import store
import query
import report
import importer

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

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        'add': cmd_add, 'list': cmd_list, 'done': cmd_done,
        'report': cmd_report, 'export': cmd_export, 'import': cmd_import,
    }
    cmds[args.command](args)

if __name__ == '__main__':
    main()
