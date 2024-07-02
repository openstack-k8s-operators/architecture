# Configuring networking and deploy the OpenStack control plane

## Assumptions

- Operators are already deployed
- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the ipv6_ironic directory
```
cd architecture/examples/dt/ipv6_ironic
```
Edit the [control-plane/networking/nncp/values.yaml](control-plane/neworking/nncp/values.yaml) file to suit your environment.
```
vi control-plane/networking/nncp/values.yaml
```

## Apply node network configuration

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
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking and configuration

Generate the networking CRs.
```
kustomize build control-plane/networking > networking.yaml
```
Apply the CRs
```
oc apply -f networking.yaml
```

## Apply the control-plane configurastion

Generate the control-plane CRs.
```
kustomize build control-plane > control-plane.yaml
```
Apply the CRs
```
oc apply -f control-plane.yaml
```
Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
