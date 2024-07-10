# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the osasinfra directory
```
cd architecture/examples/dt/osasinfra
```
Edit the [control-plane/nncp/values.yaml](control-plane/nncp/values.yaml) file to suit your environment.
```
vi control-plane/nncp/values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build control-plane/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=5m
```

## Apply networking and control-plane configuration

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
oc wait osctlplane controlplane --for condition=Ready --timeout=60m
```
