# Automation files

## Schema validation
The files are tested using `yamale`. Be sure to update
the `.ci/automation-schema.yaml` file at the root of this
project if you add a new key, or modify a type!

More information about [yamale](https://github.com/23andMe/Yamale).

## Manually check schema
```Bash
$ pip install yamale
$ yamale -s .ci/automation-schema.yaml automation/vars
```
