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

## Structure and Content

The `MkDocs` output generates nice looking HTML pages that link to the
content genereated by github.com.

This is because the authors believe it's more valuable to have
[github.com/openstack-k8s-operators/architecture](https://github.com/openstack-k8s-operators/architecture)
be navigable relative to the github pages which contain the CRs,
than have all of the documentation isolated in the `docs` directory.
Thus, there are non-relative links in the `MkDocs` content to the
pages hosted on github.

Though it's
[possible](https://www.mkdocs.org/user-guide/writing-your-docs/#linking-to-pages)
to create symbolic links to README files or link to a directory above
the `docs` directory, the resulting HTML will contain invalid links
unless all READMEs are moved out of the directories that they
describe. However, this would make reading the CRs more complicated as
they wouldn't have a corresponding README.

Thus, if you add a new VA or DT, then please just link it in the
`mkdocs.yml` file, similar to the way the HCI VA is linked, in to keep
the `MkDocs` output up to date.
