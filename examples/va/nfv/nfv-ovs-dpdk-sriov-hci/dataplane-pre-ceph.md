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
cd architecture/examples/va/nfv/nfv-ovs-dpdk-sriov-hci
```
Edit the [edpm-pre-ceph/nodeset/values.yaml](edpm-pre-ceph/nodeset/values.yaml) file to suit
your environment.
```
vi edpm-pre-ceph/nodeset/values.yaml
```
Generate the pre-Ceph dataplane nodeset CR.
```
kustomize build edpm-pre-ceph/nodeset > dataplane-nodeset-pre-ceph.yaml
```
Generate the pre-Ceph dataplane deployment CR.
```
kustomize build edpm-pre-ceph/deployment > dataplane-deployment-pre-ceph.yaml
```

## Create pre-Ceph CRs

Create the nodeset CR
```
oc apply -f dataplane-nodeset-pre-ceph.yaml
```
Wait for pre-Ceph dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment-pre-ceph.yaml
```

Wait for pre-Ceph dataplane deployment to finish
```
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=1200s
```
