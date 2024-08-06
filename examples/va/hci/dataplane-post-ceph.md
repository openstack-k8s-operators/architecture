# Configuring and deploying the post-Ceph dataplane

## Assumptions

- The pre-Ceph [dataplane](dataplane-pre-ceph.md) was already deployed and Ceph was manually installed afterwords

## Initialize post-Ceph

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the hci directory
```
cd architecture/examples/va/hci
```
Edit the [values.yaml](values.yaml) and [service-values.yaml](service-values.yaml)
files to suit your environment.
```
vi values.yaml
vi service-values.yaml
```
The ceph sections of [values.yaml](values.yaml) should have values like this.
```yaml
data:
  ceph:
    conf: $CONF
    keyring: $KEY
  nova:
    ceph:
      conf: |
        [libvirt]
        images_type=rbd
        images_rbd_pool=vms
        images_rbd_ceph_conf=/etc/ceph/ceph.conf
        images_rbd_glance_store_name=default_backend
        images_rbd_glance_copy_poll_interval=15
        images_rbd_glance_copy_timeout=600
        rbd_user=openstack
        rbd_secret_uuid=$FSID

```
Where the values of the three variables above can be retrieved by
running the following commands on the Ceph cluster.
```shell
CONF=$(cat /etc/ceph/ceph.conf | base64 -w 0)
KEY=$(cat /etc/ceph/ceph.client.openstack.keyring | base64 -w 0)
FSID=$(awk -F ' = ' '/fsid/ {print $2}' /etc/ceph/ceph.conf)
```

Generate the post-Ceph dataplane nodeset CR.
```
kustomize build > nodeset-post-ceph.yaml
```
Generate the post-Ceph dataplane deployment CR.
```
kustomize build deployment > deployment-post-ceph.yaml
```

## Create post-Ceph CRs

Create the nodeset CR
```
oc apply -f nodeset-post-ceph.yaml
```
Wait for post-Ceph dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```
Create the deployment CR
```
oc apply -f deployment-post-ceph.yaml
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

## Final OpenStackDataPlaneNodeSet services list

The `OpenStackDataPlaneNodeSet` must contain the full `services` list
so that during updates all required services are updated. Thus, the
pre-ceph and post-ceph deployments used a `servicesOverride` so that
only a subset of the services would be configured either before or
after Ceph was deployed. Any subsequent deployments should not pass a
`servicesOverride` unless necessary.
