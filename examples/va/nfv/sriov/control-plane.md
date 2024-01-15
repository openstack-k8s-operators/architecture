# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/sriov directory
```
cd architecture/examples/va/nfv/sriov
```
Edit the [values.yaml](values.yaml) and
[service-values.yaml](service-values.yaml) files to suit 
your environment.
```
vi values.yaml
vi service-values.yaml
```
Alternatively use your own copies of those files and edit
[kustomization.yaml](kustomization.yaml) to use those copies.
```
resources:
  - values-ci-framework.yaml
  - service-values-ci-framework.yaml
```

Generate the control-plane and networking CRs.
```
kustomize build > control-plane.yaml
```

## Create CRs
```
oc apply -f control-plane.yaml
```

Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

## Workaround

The `control-plane.yaml` file contains CRs for both `NMState` and
`NodeNetworkConfigurationPolicy` (NNCP). When `oc apply -f` is
passed this file, OpenShift might try to create the NNCPs while
`NMState` CRDs are still installing and produce the following message.

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
Retrying `oc apply -f contol-plane.yaml` a few seconds later should
resolve the problem however.
