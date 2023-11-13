Contributing to documentation
=============================

## Rendering documentation locally

Install docs build requirements into virtualenv:

```
python3 -m venv local/docs-venv
source local/docs-venv/bin/activate
pip install -r docs/doc_requirements.txt
```

Serve docs site on localhost:

```
mkdocs serve
```

Click the link it outputs. As you save changes to files modified in your editor,
the browser will automatically show the new content.
