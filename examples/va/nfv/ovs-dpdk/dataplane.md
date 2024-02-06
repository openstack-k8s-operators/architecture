# Configuring networking and deploy the OpenStack control plane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/ovs-dpdk/edpm directory
```
cd architecture/examples/va/nfv/ovs-dpdk/edpm
```
Edit the [values.yaml](values.yaml) file to suit 
your environment.
```
vi values.yaml
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
