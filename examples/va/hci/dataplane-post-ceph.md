# Configuring networking and deploy the OpenStack control plane

## Assumptions

- The pre-Ceph [dataplane](dataplane-pre-ceph.md) was already deployed and Ceph was manually installed afterwords

## Initialize post-Ceph

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the hci/edpm-post-ceph directory
```
cd architecture/examples/va/hci/edpm-post-ceph
```
Edit the [values.yaml](values.yaml) and [service-values.yaml](service-values.yaml) 
files to suit your environment.
```
vi values.yaml
vi service-values.yaml
```
Generate the post-Ceph dataplane CRs.
```
kustomize build > dataplane-post-ceph.yaml
```

## Create post-Ceph CRs
```
oc apply -f dataplane-post-ceph.yaml
```

Wait for control plane to be available after updating
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

Wait for post-Ceph dataplane deployment to finish
```
oc wait osdpd edpm-deployment-post-ceph --for condition=Ready --timeout=1200s
```

## Finalize Nova computes

Ask Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
