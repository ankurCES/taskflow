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

if __name__ == '__main__':
    unittest.main()
