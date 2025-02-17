# Configuring networking and deploy the OpenStack control plane


## Assumptions

- A storage class called `local-storage` should already exist.


## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the uni05epsilon directory

```bash
cd architecture/examples/dt/uni05epsilon
```

Edit [control-plane/service-values.yaml](control-plane/service-values.yaml) and
[control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml).

## Apply node network configuration

Generate the node network configuration
```bash
kustomize build control-plane/networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s
```

## Apply remaining networking configuration

Generate the reminaing networking configuration
```
kustomize build control-plane/networking > networking.yaml
```
Apply the networking CRs
```
oc apply -f networking.yaml
```

## Apply the control-plane configuration.

Generate the control-plane CRs.
```bash
kustomize build control-plane/ > control-plane.yaml
```
Apply the CRs
```bash
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```bash
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
