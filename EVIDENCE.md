# Evidence Log

## Phase 1 — Plan on the board (2026-07-03T16:58Z)

**Board tree with IDs + dependencies:**

```
Epic: taskflow v0
  id: 41428033-150a-4de3-bdde-05b275c2b5d9
  status: todo

  └─ Story: core modules
     id: e2946dd5-805a-4765-bc24-b1f331ce85c4
     status: todo
     acceptance_criteria:
       - models.py has Project and Task dataclasses + validate_task
       - store.py does atomic JSON persistence with tmp+rename
       - query.py has by_status, by_project, overdue, search, next_up
       - report.py produces aligned text table + self-contained HTML dashboard
       - importer.py handles CSV import/export with header tolerance
       - taskflow.py CLI wires all modules with argparse
       - test_taskflow.py passes all integration tests

     ├─ Task: models.py        id: 3d942e57-e78c-4384-9607-722194fa76ee  deps: []
     ├─ Task: store.py         id: 803503ff-c192-4f2d-a741-778f85c09e10  deps: []
     ├─ Task: query.py         id: 4d16d700-47b0-44a6-bdfc-aef09e15e1e0  deps: []
     ├─ Task: report.py        id: 97b11899-5107-4052-98c6-038f3f847172  deps: []
     ├─ Task: importer.py      id: 7dacd200-54bd-4f7e-8a05-3bad1611ab9f  deps: []
     └─ Task: CLI + integration tests
        id: 2b0cee62-df58-4402-8262-dececf7aff8c
        deps: [3d942e57, 803503ff, 4d16d700, 97b11899, 7dacd200]
        (blocked until all 5 module tasks are done)
```

All 5 module tasks are independent (no inter-dependencies). Task 6 depends on all 5.
