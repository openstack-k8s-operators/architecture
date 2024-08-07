# Getting your PR into a stable branch

After your PR merges into the main branch you should open a PR to
cherry pick it into a stable branch if appropriate. For example,
you may want your patch to be in the
[18.0.0-proposed branch](https://github.com/openstack-k8s-operators/architecture/tree/18.0.0-proposed).

If you anticipate that your PR should be cherry picked then please tag
it accordingly. For example we have a
[needs-18.0.0-proposed-cherry-pick](https://github.com/openstack-k8s-operators/architecture/issues?q=label%3Aneeds-18.0.0-proposed-cherry-pick+)
tag. If we think a patch should be in a stable branch, then we will
apply that tag to your PR to remind you to follow up to send in a
cherry pick.

Please do not ask [core maintainers](../../OWNERS) to cherry pick your
patch though we will be happy to review it and help merge it once the
cherry pick PR has been submitted.

If you can send a PR to this repository then you can create a cherry
pick using the `git` command line tools without requiring any
additional privileges. For example, the following produces a
cherry-pick within a personal fork of the architecture repository.
```
git remote add upstream git@github.com:openstack-k8s-operators/architecture.git 
git fetch upstream
git checkout -b 18.0.0-proposed upstream/18.0.0-proposed
git push origin 18.0.0-proposed
git log origin/main
git cherry-pick <commit hash>
git push origin 18.0.0-proposed
```
You should then be able to use the github web interface to create the
PR. Please add `(cherry picked from <commit hash>)` to the bottom of
your commit message.
