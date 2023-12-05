# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to "openstack" namespace
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
[kustomization.yaml](kustomization.yaml) to use a that copy.
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

Wait for NNCPs to be available
```
oc wait nncp -l nncm-config-type=standard --for condition=available --timeout=300s
```

### Todo
- Update `../../../lib/networking/netconfig.yaml` to use kustomize
- Update `../../../lib/networking/netattach_*` to use kustomize
- This is a place holder until the READMEs is moved to [docs](../../../docs/)


