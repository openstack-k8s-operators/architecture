# Configuring networking and deploy the OpenStack control plane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize pre-Ceph

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the hci/edpm-pre-ceph directory
```
cd architecture/examples/va/hci/edpm-pre-ceph
```
Edit the [values.yaml](values.yaml) file to suit 
your environment.
```
vi values.yaml
```
Generate the pre-Ceph dataplane CRs.
```
kustomize build > dataplane-pre-ceph.yaml
```

## Create pre-Ceph CRs
```
oc apply -f dataplane-pre-ceph.yaml
```

Wait for pre-Ceph dataplane deployment to finish
```
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=1200s
```
