# Opening pull requests

Contributions to the `architecture` repository are always welcomed and
encouraged. In order to avoid causing regressions to the repository and to
prove that the contributions are working as intended, all pull requests are
expected to provide proof of validation.

The simplest way is to use the reproducer functionality in the
[CI-Framework](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html).

## Using the reproducer role

Additional parameters can be passed to the reproducer role of the CI-Framework,
allowing you validate changes to the architecture repository remain functional
within the contexts of kustomize and CI-Framework itself (which consumes the
contents of the architecture repository).

Use the `reproducer.yml` playbook within the CI-Framework to deploy the HCI
validated architecture aka VA1 (or any other validated architecture or
deployment topology that might be affected) with an environment file containing
parameters denoting which branch and repository to deploy with. The custom
parameter filename is not important, as long as it is passed to Ansible, and is
valid.

```bash
ansible-playbook reproducer.yml \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/va-hci.yml \
    -e @scenarios/reproducers/networking-definition.yml \
    -e @custom/default-vars.yaml \
    -e @custom/secrets.yml \
    -e @custom/test-my_pr_branch.yml
```

The `test-my_pr_branch.yml` file contains parameters that identifies the remote
git repository and branch name to deploy.

**test-my_pr_branch.yml**

```yaml
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
- src: "https://github.com/<FORKED_ORGANIZATION>/architecture"
  dest: "{{ remote_base_dir }}/architecture"
  version: <BRANCH_TO_DEPLOY>
```

Once your environment has been deployed, provide any relevant output showing
that the deployment was successful, and that the environment continues to
operate nominally. Provide any additional output showing that the changes to
the architecture repository have been deployed and are functioning as intended
by the pull request. You can SSH into the controller-0 machine and review the
contents of `/home/zuul/src/github.com/openstack-k8s-operators/architecture`
which contains the content as configured by the `test-<NAME>.yml` parameter
file.
