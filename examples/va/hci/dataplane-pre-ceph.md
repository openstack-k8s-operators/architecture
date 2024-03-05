# Configuring and deploying the pre-Ceph dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize pre-Ceph

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the hci directory
```
cd architecture/examples/va/hci
```
Edit the [edpm-pre-ceph/values.yaml](edpm-pre-ceph/values.yaml) file to suit 
your environment.
```
vi edpm-pre-ceph/values.yaml
```
Generate the pre-Ceph dataplane CRs.
```
kustomize build edpm-pre-ceph > dataplane-pre-ceph.yaml
```

## Create pre-Ceph CRs
```
oc apply -f dataplane-pre-ceph.yaml
```

Wait for pre-Ceph dataplane deployment to finish
```
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=1200s
```
