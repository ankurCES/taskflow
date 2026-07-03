# EVIDENCE-2.md — taskflow v1 Grid Integration Run

## Phase 0 — Sync (2026-07-03)

```
$ git pull origin main
Already up to date.

$ git status -sb
## main...origin/main
?? __pycache__/
```

**Verdict:** Clean, in sync with origin. Remote peers will clone at HEAD = `ed2be86`.

---

## Phase 1 — Plan v1 (2026-07-03)

### Board tree

```
Epic: taskflow v1 (2dbeddd7)
  └─ Story: power features (a7e48606)
       ├─ Task: reminders.py   (2577743c) [todo, no deps]
       ├─ Task: stats.py       (5d9ea38b) [todo, no deps]
       ├─ Task: archive.py     (769e4872) [todo, no deps]
       ├─ Task: tags.py        (1b15f818) [todo, no deps]
       ├─ Task: validate.py    (7ed8be58) [todo, no deps]
       └─ Task: v1 CLI + tests (a3ba1061) [todo, depends on all 5 above]
```

5 independent tasks → grid-parallelizable. Task 6 blocked until all 5 done.

**Verdict:** Board structure matches plan. Ready for grid fanout.

---

## Phase 2 — Grid Fanout (2026-07-03)

### Fanout call

```
lumi_sprint_grid_fanout(budget_secs=600, blocking=true)
```

### Response

```json
{"dispatched": 5, "mode": "blocking", "results": [
  {"id": "1b15f818 (tags.py)",       "ok": true},
  {"id": "2577743c (reminders.py)",   "ok": true},
  {"id": "5d9ea38b (stats.py)",       "ok": true},
  {"id": "769e4872 (archive.py)",     "ok": true},
  {"id": "7ed8be58 (validate.py)",    "ok": true}
]}
```

### repo_mode

The fanout response did not include an explicit `repo_mode` field. However, **repo_mode was active**: three tasks produced "applied as commit" lines in their grid comments, confirming peers worked in real git checkouts and diffs were auto-committed locally. The two failures were not repo_mode failures — they were `git apply` failures caused by binary `.pyc` files included in the patches.

### Task → Peer Map

| Task | Peer | Result |
|------|------|--------|
| tags.py | mac-mini-slave (Ankurs-Mac-mini.local) | applied as commit `cbf41d6` |
| validate.py | mac-mini-slave (Ankurs-Mac-mini.local) | applied as commit `b96d26b` |
| archive.py | mac-mini-slave (Ankurs-Mac-mini.local) | applied as commit `1b826f7` |
| stats.py | predator-blum (ankur-Predator-PHN16S-71) | DIFF NOT APPLIED — binary .pyc |
| reminders.py | nvidia-jetson (openclaw-jet) | DIFF NOT APPLIED — binary .pyc |

### Peer distribution

- **mac-mini-slave**: 3 tasks (tags, validate, archive)
- **predator-blum**: 1 task (stats)
- **nvidia-jetson**: 1 task (reminders)
- 5 tasks across 3 peers (not 4 as expected). No "peer busy — reassign me" bounces observed.

### DIFF NOT APPLIED handling

Both failed patches saved at:
- `.lumi/grid-diffs/5d9ea38b-c960-42e5-b50b-caed73bb226e.patch` (stats.py)
- `.lumi/grid-diffs/2577743c-1ce6-4f86-9dbc-83d72684e2a6.patch` (reminders.py)

Applied manually with: `git apply --3way --exclude='__pycache__/*'`
Committed as `ec6926d`.

---

## Phase 3 — Local Work (2026-07-03)

Wrote `docs/V1-DESIGN.md` (interfaces of all 5 new modules) while grid peers ran.

Committed as `c594ac4`. Grid comments timestamped 18:19–18:21, local doc committed same window — confirms overlap.

---

## Phase 4 — Collect (2026-07-03)

### Per-task grid evidence

| Task | Peer | Comment excerpt |
|------|------|-----------------|
| tags.py | [grid:mac-mini-slave] | "applied as commit cbf41d6" — 14-case smoke test passed |
| validate.py | [grid:mac-mini-slave] | "applied as commit b96d26b" — 8-case smoke test passed |
| archive.py | [grid:mac-mini-slave] | "applied as commit 1b826f7" — 7-case smoke test passed |
| stats.py | [grid:predator-blum] | "DIFF NOT APPLIED" — patch saved, manually applied as `ec6926d` |
| reminders.py | [grid:nvidia-jetson] | "DIFF NOT APPLIED" — patch saved, manually applied as `ec6926d` |

### git log showing grid-authored commits

```
$ git log --oneline -12
c594ac4 Phase 3: V1 design doc (local work while grid peers ran)
ec6926d Manually apply stats.py + reminders.py from grid patches (--exclude __pycache__)
cbf41d6 grid(mac-mini-slave): tags.py
b96d26b grid(mac-mini-slave): validate.py
1b826f7 grid(mac-mini-slave): archive.py
3a89fb8 Phase 0+1 evidence: sync confirmed, board tree with 5 independent tasks + 1 dependent
ed2be86 Phase 6: final evidence — all tasks done, 9/9 tests green
1745722 Phase 5: CLI + integration tests + dashboard (9/9 tests pass)
6fdbe7a Add 5 core modules (reconciled from grid peer work — diffs not auto-applied)
9e1f6e7 Phase 2+3 evidence: grid fanout + local docs overlap
b39d018 Phase 3: add architecture and usage docs (local work while grid runs)
664f088 Phase 1: board plan with epic, story, 6 tasks
```

**Verdict:** All 5 modules collected. 3 grid-auto-committed, 2 manually patched. Ready for Phase 5.

---

