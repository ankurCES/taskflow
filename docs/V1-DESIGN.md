# taskflow v1 — Module Interfaces

## reminders.py

```python
due_soon(tasks: list[dict], today: str, days: int = 3) -> list[dict]
```
Returns tasks with due date within `days` of `today` (YYYY-MM-DD), excluding done.

```python
overdue_summary(tasks: list[dict], today: str) -> str
```
Multi-line string of overdue tasks: `[{id}] {title} (due {due})`. Returns `"No overdue tasks."` if none.

## stats.py

```python
completion_rate(tasks: list[dict]) -> float
```
Fraction done. 0.0 if empty.

```python
by_tag_counts(tasks: list[dict]) -> dict[str, int]
```
Tag → count across all tasks.

```python
velocity(tasks: list[dict], done_dates: dict[str, str], weeks: int = 4) -> float
```
Tasks completed per week over last `weeks` weeks. 0.0 if no done_dates.

## archive.py

```python
archive_done(data: dict, archive_path: str) -> None
```
Moves done tasks from `data['tasks']` to `archive_path` JSON (`{"archived": [...]}`). In-place.

```python
restore(data: dict, archive_path: str, task_id: str) -> None
```
Moves task back from archive to `data['tasks']`. Raises `ValueError` if not found.

## tags.py

```python
rename_tag(tasks: list[dict], old: str, new: str) -> None
```
In-place rename. Deduplicates if `new` already present.

```python
merge_tags(tasks: list[dict], tag_a: str, tag_b: str) -> None
```
Merge `tag_b` into `tag_a`. Delegates to `rename_tag`.

```python
tag_counts(tasks: list[dict]) -> dict[str, int]
```
Tag → count.

## validate.py

```python
lint(data: dict) -> list[str]
```
Returns list of error strings. Checks: duplicate ids, dangling project_ids, bad due dates, priority out of range (1-5).
