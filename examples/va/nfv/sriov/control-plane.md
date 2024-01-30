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
