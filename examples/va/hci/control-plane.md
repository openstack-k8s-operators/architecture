# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the hci directory
```
cd architecture/examples/va/hci
```
Edit the [values.yaml](values.yaml) file to suit your environment.
```
vi values.yaml
```
Alternatively use your own copy of `values.yaml` and edit 
[kustomization.yaml](kustomization.yaml) to use that copy.
```
resources:
  - values-ci-framework.yaml
```

Generate the control-plane and networking CRs.
```
kustomize build > control-plane.yaml
```

## Create CRs
```
oc apply -f control-plane.yaml
```
If the `oc apply` command produces a `no matches for kind
NodeNetworkConfigurationPolicy` error, then see,
[Missing NNCPs Workaround](../../docs/wa/missing_nncp.md).

Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
