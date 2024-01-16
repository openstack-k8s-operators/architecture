# Missing NNCPs

The kustomize command builds and results in the OpenStack control
plane definitions and its dependent Custom Resources (CR).
```bash
kustomize build architecture/examples/va/hci > control-plane.yaml
```
The `control-plane.yaml` file contains CRs for both `NMState` and
`NodeNetworkConfigurationPolicy` (NNCP). When  `oc apply -f
control-plane.yaml` is read, OpenShift will try to create the NNCPs
while `NMState` Custom Resource Definitions (CRD) are still installing
and produce a message noting that the resource mappings are not found:
```
nmstate.nmstate.io/nmstate created
[resource mapping not found for name:
"ostest-master-0" namespace: "openstack" from "control-plane.yaml":
no matches for kind "NodeNetworkConfigurationPolicy" in version "nmstate.io/v1"
ensure CRDs are installed first,
resource mapping not found for name: "ostest-master-1" namespace: "openstack"
from "control-plane.yaml": no matches for kind "NodeNetworkConfigurationPolicy"
in version "nmstate.io/v1"
```
Retrying `oc apply -f contol-plane.yaml` a few seconds later is likely to
resolve the problem.

## Alternative Approach

It's also possible to create CR files with less components and wait
before applying each CR file. E.g. the file `nncp.yaml` would contain
only `NodeNetworkConfigurationPolicy` CRs and `NMState` and other
deployment related CRs could exist in another file like
`deploy.yaml`. The following process may be used to do generate these
files using kustomize.

- Modify the
[va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
file so that the last two lines contain only the deploy component
configuration:
```yaml
components:
- ../../lib/deploy
```
- Generate a file with only `MetalLB` and `NMState` CRs:
```bash
kustomize build architecture/examples/va/hci > deploy.yaml
```
- Modify the
[va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
file so that the last two lines contain only the nncp component
configuration:
```yaml
components:
- ../../lib/nncp
```
- Generate a file with only `NNCP` CRs:
```bash
kustomize build architecture/examples/va/hci > nncp.yaml
```
The above process may be continued for each component.

Note that [va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
is not the same file as
[examples/va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/examples/va/hci/kustomization.yaml).
`/example/va/hci` is a specific example of a given VA where as
`/va/hci` is a generic HCI VA that may be customised and shared in
multiple examples or composed to make a larger VA.

This process will work for VAs (and DTs) besides HCI, but the paths
may be different. E.g.
[examples/va/nfv/sriov/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/examples/va/nfv/sriov/kustomization.yaml)
differs from
[va/nfv/sriov/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/nfv/sriov/kustomization.yaml)
and the later is in an `nfv` subdirectory
so each component is referred to using
`- ../../../lib/` instead of `- ../../lib/`.
