# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the perfscale/scalelab directory
```
cd architecture/examples/dt/perfscale/scalelab
```
Edit the [networking/nncp/values.yaml](networking/nncp/values.yaml) and
[service-values.yaml](service-values.yaml) files to suit 
your environment.
```
vi networking/nncp/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build networking/nncp > nncp.yaml
```

Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply remaining networking configuration

Generate the remaining network configuration
```
kustomize build networking > networking.yaml
```
Apply the networking CRs
```
oc apply -f networking.yaml
```

## Apply the control-plane configuration

Generate the control-plane CRs.
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