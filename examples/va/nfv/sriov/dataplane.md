# Configuring networking and deploy the OpenStack control plane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/sriov/edpm directory
```
cd architecture/examples/va/nfv/sriov/edpm
```
Edit the [values.yaml](values.yaml) file to suit 
your environment.
```
vi values.yaml
```
Alternatively use your own copies of those files and edit
[kustomization.yaml](kustomization.yaml) to use those copies.
```
resources:
  - values-ci-framework.yaml
```

Generate the dataplane CRs.
```
kustomize build > dataplane.yaml
```

## Create CRs
```
oc apply -f dataplane.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment --for condition=Ready --timeout=1200s
```
