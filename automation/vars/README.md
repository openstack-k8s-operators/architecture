# Automation files

## Schema validation
The files are tested using `yamale`. Be sure to update
the `.ci/automation-schema.yaml` file at the root of this
project if you add a new key, or modify a type!

More information about [yamale](https://github.com/23andMe/Yamale).

### Manually check schema
```Bash
$ pip install yamale
$ yamale -s .ci/automation-schema.yaml automation/vars
```

## Adding a new automation scenario

You have to ensure new CI job is create for your new scenario.

You can generate the new job running the `create-zuul-jobs.py`
script located at the root of this repository.

The script requires `pyyaml`.

The Zuul job supports `Depends-On` in case your new scenario needs specific
data from the CI Framework (usually in the
[ci_gen_kustomize_values](https://ci-framework.readthedocs.io/en/latest/roles/ci_gen_kustomize_values.html)
role).

### Manually validating your scenario: CI Framework

The [CI Framework](https://github.com/openstack-k8s-operators/ci-framework) project is
able to consume the automation files. Therefore, it can be used in order to ensure
the various pieces are working together.

#### Read-only build

The Framework provides a playbook able to run against the automation, and build the CRs.
This is reflected in the Zuul CI tests associated to this project, like
`rhoso-architecture-validate-hci`.

If you want to manually test using the CI Framework before proposing a new scenario automation,
you can run the following:
```Bash
$ cd ci-framework
$ make run_ctx_architecture_test \
    SCENARIO_NAME=your_scenario \
    ARCH_REPO=../architecture  \
    NET_ENV_FILE=./ci/playbooks/files/networking-env-definition.yml
```
You have to install `podman` to run this - everything will run in a container.

You can find the built CRs in `~/ci-framework-data/your_scenario/artifacts/`.
