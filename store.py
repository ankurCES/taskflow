import json
import os
import tempfile

def load(path):
    if not os.path.exists(path):
        return {"projects": [], "tasks": []}
    with open(path, 'r') as f:
        return json.load(f)

def save(data, path):
    directory = os.path.dirname(path) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        os.rename(tmp_path, path)
    except:
        os.unlink(tmp_path)
        raise
