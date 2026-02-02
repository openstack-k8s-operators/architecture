# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nova/nova02beta/networking directory
```
cd architecture/examples/dt/nova/nova02beta/networking/
```
Edit the [nncp/values.yaml](networking/nncp/values.yaml)
```
vi nncp/values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Create NAD's, IPAddressPool, and NetConfig

Generate Network attachment definitions, IPAddressPools and remaining 
networking CRs. Note that the associated values for these resources are also
defined in [nncp/values.yaml](networking/nncp/values.yaml)
```
kustomize build > network.yaml
```
Apply the CRs
```
oc apply -f network.yaml
```

Wait for networking resources to be available
```
oc -n metallb-system wait pod -l app=metallb -l component=speaker --for condition=Ready --timeout=5m
```

## Create control-plane configuration

Change to the architecture/examples/dt/nova/nova02beta directory
```
cd architecture/examples/dt/nova/nova02beta
```
Edit the [service-values.yaml](service-values.yaml) files to suit your
environment.
```
vi service-values.yaml
```

## Apply control-plane configuration

Generate the control-plane and networking CRs.
```
kustomize build > control-plane.yaml
```
Apply the CRs
```
oc apply -f control-plane.yaml
```
Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```