# Missing NNCPs

The kustomize command builds and results in the OpenStack control plane definitions and its
dependent Custom Resources (CR).
```bash
kustomize build architecture/examples/va/hci > control-plane.yaml
```
The `control-plane.yaml` file contains CRs for both `NMState` and
`NodeNetworkConfigurationPolicy` (NNCP). When  `oc apply -f control-plane.yaml` is read, OpenShift will try to create the NNCPs while `NMState`
Custom Resource Definitions (CRD) are still installing and produce a message noting that the resource mappings are not found:
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

You can create Custom Resource (CR) files with less components and wait
before applying each CR file. For example, the file `nncp.yaml` could contain
only `NodeNetworkConfigurationPolicy` CRs and `NMState` definitions. Other
deployment related CRs could exist in another file such as
`deploy.yaml`. You can generate these files using kustomize.

- Modify the [va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml) file for your environment
so that the last two lines contain the deploy component configuration:
```yaml
components:
- ../../lib/deploy
