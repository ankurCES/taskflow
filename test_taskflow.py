#!/usr/bin/env python3
import unittest
import os
import tempfile
import store
import query
import report
import importer

class TestRoundtrip(unittest.TestCase):
    def test_add_save_load(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        try:
            data = store.load(path)
            self.assertEqual(data, {"projects": [], "tasks": []})
            task = {
                'id': 't1', 'project_id': 'p1', 'title': 'Test task',
                'priority': 1, 'status': 'todo', 'due': '2026-07-10',
                'tags': ['test', 'demo']
            }
            data['projects'].append({'id': 'p1', 'name': 'Demo'})
            data['tasks'].append(task)
            store.save(data, path)
            loaded = store.load(path)
            self.assertEqual(len(loaded['tasks']), 1)
            self.assertEqual(loaded['tasks'][0]['title'], 'Test task')
            self.assertEqual(loaded['projects'][0]['name'], 'Demo')
        finally:
            os.unlink(path)

class TestQuery(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {'id': 't1', 'project_id': 'p1', 'title': 'Design', 'priority': 1,
             'status': 'todo', 'due': '2026-06-01', 'tags': ['design']},
            {'id': 't2', 'project_id': 'p1', 'title': 'Build API', 'priority': 2,
             'status': 'in_progress', 'due': '2026-08-01', 'tags': ['backend']},
            {'id': 't3', 'project_id': 'p2', 'title': 'Write docs', 'priority': 3,
             'status': 'done', 'due': '2026-05-01', 'tags': ['docs']},
            {'id': 't4', 'project_id': 'p2', 'title': 'Deploy', 'priority': 1,
             'status': 'todo', 'due': None, 'tags': ['ops', 'deploy']},
        ]

    def test_overdue(self):
        result = query.overdue(self.tasks, '2026-07-03')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 't1')

    def test_search(self):
        result = query.search(self.tasks, 'deploy')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 't4')
        result2 = query.search(self.tasks, 'API')
        self.assertEqual(len(result2), 1)

    def test_next_up(self):
        result = query.next_up(self.tasks, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['priority'], 1)
        self.assertNotEqual(result[0]['status'], 'done')

    def test_by_status(self):
        result = query.by_status(self.tasks, 'todo')
        self.assertEqual(len(result), 2)

    def test_by_project(self):
        result = query.by_project(self.tasks, 'p2')
        self.assertEqual(len(result), 2)

class TestCSV(unittest.TestCase):
    def test_csv_roundtrip(self):
        tasks = [
            {'id': 't1', 'project_id': 'p1', 'title': 'Test', 'priority': 1,
             'status': 'todo', 'due': '2026-07-10', 'tags': ['a', 'b']},
            {'id': 't2', 'project_id': 'p2', 'title': 'Other', 'priority': 2,
             'status': 'done', 'due': None, 'tags': []},
        ]
        csv_text = importer.to_csv(tasks)
        parsed = importer.from_csv(csv_text)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['title'], 'Test')
        self.assertEqual(parsed[0]['tags'], ['a', 'b'])
        self.assertEqual(parsed[1]['due'], None)

class TestReport(unittest.TestCase):
    def test_html_contains_project_names(self):
        data = {
            'projects': [{'id': 'p1', 'name': 'Alpha'}, {'id': 'p2', 'name': 'Beta'}],
            'tasks': [
                {'id': 't1', 'project_id': 'p1', 'title': 'Task A',
                 'priority': 1, 'status': 'todo', 'due': None, 'tags': []},
                {'id': 't2', 'project_id': 'p2', 'title': 'Task B',
                 'priority': 2, 'status': 'done', 'due': '2026-07-01', 'tags': []},
            ]
        }
        html = report.html_report(data)
        self.assertIn('Alpha', html)
        self.assertIn('Beta', html)
        self.assertIn('Taskflow Dashboard', html)

    def test_summary_table(self):
        data = {
            'projects': [{'id': 'p1', 'name': 'Alpha'}],
            'tasks': [
                {'id': 't1', 'project_id': 'p1', 'title': 'X',
                 'priority': 1, 'status': 'todo', 'due': None, 'tags': []},
            ]
        }
        text = report.summary(data)
        self.assertIn('Alpha', text)
        self.assertIn('todo', text)

class TestReminders(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {'id': 't1', 'title': 'Soon', 'status': 'todo', 'due': '2026-07-05', 'tags': []},
            {'id': 't2', 'title': 'Far', 'status': 'todo', 'due': '2026-08-01', 'tags': []},
            {'id': 't3', 'title': 'Done', 'status': 'done', 'due': '2026-07-04', 'tags': []},
            {'id': 't4', 'title': 'Overdue', 'status': 'todo', 'due': '2026-06-01', 'tags': []},
            {'id': 't5', 'title': 'NoDue', 'status': 'todo', 'due': None, 'tags': []},
        ]

    def test_due_soon_default(self):
        import reminders
        result = reminders.due_soon(self.tasks, '2026-07-03')
        ids = [t['id'] for t in result]
        self.assertIn('t1', ids)
        self.assertNotIn('t2', ids)
        self.assertNotIn('t3', ids)

    def test_due_soon_excludes_done(self):
        import reminders
        result = reminders.due_soon(self.tasks, '2026-07-03')
        self.assertTrue(all(t['status'] != 'done' for t in result))

    def test_overdue_summary(self):
        import reminders
        result = reminders.overdue_summary(self.tasks, '2026-07-03')
        self.assertIn('t4', result)
        self.assertIn('Overdue', result)

    def test_overdue_none(self):
        import reminders
        result = reminders.overdue_summary([], '2026-07-03')
        self.assertEqual(result, "No overdue tasks.")


class TestStats(unittest.TestCase):
    def test_completion_rate(self):
        import stats
        tasks = [{'status': 'done'}, {'status': 'todo'}, {'status': 'done'}]
        self.assertAlmostEqual(stats.completion_rate(tasks), 2/3)

    def test_completion_rate_empty(self):
        import stats
        self.assertEqual(stats.completion_rate([]), 0.0)

    def test_by_tag_counts(self):
        import stats
        tasks = [
            {'tags': ['a', 'b']},
            {'tags': ['b', 'c']},
            {'tags': ['a']},
        ]
        counts = stats.by_tag_counts(tasks)
        self.assertEqual(counts['a'], 2)
        self.assertEqual(counts['b'], 2)
        self.assertEqual(counts['c'], 1)

    def test_velocity(self):
        import stats
        done_dates = {'t1': '2026-07-01', 't2': '2026-06-20', 't3': '2026-05-01'}
        v = stats.velocity([], done_dates, weeks=4)
        self.assertEqual(v, 0.5)

    def test_velocity_empty(self):
        import stats
        self.assertEqual(stats.velocity([], {}, weeks=4), 0.0)


class TestArchive(unittest.TestCase):
    def test_archive_and_restore(self):
        import archive
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            archive_path = f.name
        try:
            data = {'tasks': [
                {'id': 't1', 'status': 'done', 'title': 'X'},
                {'id': 't2', 'status': 'todo', 'title': 'Y'},
            ]}
            archive.archive_done(data, archive_path)
            self.assertEqual(len(data['tasks']), 1)
            self.assertEqual(data['tasks'][0]['id'], 't2')
            archive.restore(data, archive_path, 't1')
            self.assertEqual(len(data['tasks']), 2)
        finally:
            os.unlink(archive_path)

    def test_restore_not_found(self):
        import archive
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            archive_path = f.name
        try:
            data = {'tasks': [{'id': 't1', 'status': 'done', 'title': 'X'}]}
            archive.archive_done(data, archive_path)
            with self.assertRaises(ValueError):
                archive.restore(data, archive_path, 'nonexistent')
        finally:
            os.unlink(archive_path)


class TestTags(unittest.TestCase):
    def test_rename_tag(self):
        import tags
        tasks = [{'tags': ['a', 'b']}, {'tags': ['a', 'c']}]
        tags.rename_tag(tasks, 'a', 'x')
        self.assertEqual(tasks[0]['tags'], ['x', 'b'])
        self.assertEqual(tasks[1]['tags'], ['x', 'c'])

    def test_rename_dedup(self):
        import tags
        tasks = [{'tags': ['a', 'b']}]
        tags.rename_tag(tasks, 'a', 'b')
        self.assertEqual(tasks[0]['tags'], ['b'])

    def test_merge_tags(self):
        import tags
        tasks = [{'tags': ['x', 'y']}, {'tags': ['y', 'z']}]
        tags.merge_tags(tasks, 'x', 'y')
        self.assertNotIn('y', tasks[0]['tags'])
        self.assertIn('x', tasks[1]['tags'])

    def test_tag_counts(self):
        import tags
        tasks = [{'tags': ['a', 'b']}, {'tags': ['a']}]
        counts = tags.tag_counts(tasks)
        self.assertEqual(counts['a'], 2)
        self.assertEqual(counts['b'], 1)


class TestValidate(unittest.TestCase):
    def test_lint_clean(self):
        import validate
        data = {
            'projects': [{'id': 'p1', 'name': 'P'}],
            'tasks': [{'id': 't1', 'project_id': 'p1', 'priority': 3, 'due': '2026-07-01'}]
        }
        self.assertEqual(validate.lint(data), [])

    def test_lint_duplicate_ids(self):
        import validate
        data = {
            'projects': [],
            'tasks': [{'id': 't1', 'priority': 1}, {'id': 't1', 'priority': 2}]
        }
        errors = validate.lint(data)
        self.assertTrue(any('duplicate' in e for e in errors))

    def test_lint_dangling_project(self):
        import validate
        data = {
            'projects': [{'id': 'p1'}],
            'tasks': [{'id': 't1', 'project_id': 'p99', 'priority': 3}]
        }
        errors = validate.lint(data)
        self.assertTrue(any('unknown project' in e for e in errors))

    def test_lint_bad_date(self):
        import validate
        data = {
            'projects': [],
            'tasks': [{'id': 't1', 'priority': 3, 'due': 'not-a-date'}]
        }
        errors = validate.lint(data)
        self.assertTrue(any('bad due date' in e for e in errors))

    def test_lint_priority_range(self):
        import validate
        data = {
            'projects': [],
            'tasks': [{'id': 't1', 'priority': 99}]
        }
        errors = validate.lint(data)
        self.assertTrue(any('priority' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
