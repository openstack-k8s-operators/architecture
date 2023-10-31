# Stage 6

Finish deploying the data plane after Ceph is available

## Notes

Assumes that a Ceph cluster is available

## Steps

1. Create Secrets
```bash
oc apply -f ceph_secret.yaml -f nova_ceph.yaml -f nova_migration_ssh_key.yaml
```
2. Create image conversion PVC
```bash
oc apply -f image_conversion_pvc.yaml
```
3. Update OpenStackControlPlane and wait for it to finish
```bash
oc apply -f openstackcontrolplane.yaml
oc wait osctlplane openstack-galera-network-isolation-3replicas --for condition=Ready --timeout=300s
```
4. Update OpenStackDataPlaneNodeSet
```bash
oc apply -f openstackdataplanenodeset.yaml
```
5. Create a post-Ceph OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd deployment-post-ceph --for condition=Ready --timeout=720s
```
6. Force Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
