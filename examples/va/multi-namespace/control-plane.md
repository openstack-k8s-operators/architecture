# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Change to the multi-namespace directory
```
cd architecture/examples/va/multi-namespace
```

## Control plane one

Edit the [control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml) and
[control-plane/service-values.yaml](control-plane/service-values.yaml) files to suit 
your environment.
```
vi control-plane/networking/nncp/values.yaml
vi control-plane/service-values.yaml
```

### Apply node network configuration

Generate the node network configuration
```
kustomize build control-plane/networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait -n openstack nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

### Apply networking configuration

Generate the networking configuration
```
kustomize build control-plane/networking > networking.yaml
```
Apply the networking CRs
```
oc apply -f networking.yaml
```

### Apply control-plane configuration

Generate the control-plane and networking CRs.
```
kustomize build control-plane > control-plane.yaml
```
Apply the CRs
```
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```
oc wait -n openstack osctlplane controlplane --for condition=Ready --timeout=600s
```

## Control plane two

Edit the [control-plane2/networking/nncp/values.yaml](control-plane2/networking/nncp/values.yaml) and
[control-plane2/service-values.yaml](control-plane2/service-values.yaml) files to suit 
your environment.
```
vi control-plane2/networking/nncp/values.yaml
vi control-plane2/service-values.yaml
```

### Apply node network configuration

Generate the node network configuration
```
kustomize build control-plane2/networking/nncp > nncp2.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp2.yaml
```
Wait for NNCPs to be available
```
oc wait -n openstack2 nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

### Apply networking configuration

Generate the networking configuration
```
kustomize build control-plane2/networking > networking2.yaml
```
Apply the networking CRs
```
oc apply -f networking2.yaml
```

### Apply control-plane configuration

Generate the control-plane and networking CRs.
```
kustomize build control-plane2 > control-plane2.yaml
```
Apply the CRs
```
oc apply -f control-plane2.yaml
```

Wait for control plane to be available
```
oc wait -n openstack2 osctlplane controlplane --for condition=Ready --timeout=600s
