# Usage

## CLI commands

```bash
# Add a task
python taskflow.py add --project p1 --title "Design mockups" --priority 1 --due 2026-07-10 --tags design,ui

# List all tasks
python taskflow.py list

# List filtered
python taskflow.py list --status todo
python taskflow.py list --project p1

# Mark a task done
python taskflow.py done t1

# Print text summary report
python taskflow.py report

# Export tasks to CSV
python taskflow.py export

# Export as HTML dashboard
python taskflow.py export --html

# Import tasks from CSV
python taskflow.py import tasks.csv
```

## Data file

Default store location: `taskflow.json` in the current directory.

## Dependencies

Python 3 stdlib only. No pip install required.
