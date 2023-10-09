# Stage 6

Finish deploying the data plane after Ceph is available

## Notes

Assumes that a Ceph cluster is available

## Steps

1. Create Secrets
```bash
oc apply -f ceph_secret.yaml -f nova_ceph.yaml
```
2. Update OpenStackControlPlane and wait for it to finish
```bash
oc apply -f openstackcontrolplane.yaml
oc wait osctlplane openstack-galera-network-isolation-3replicas --for condition=Ready --timeout=300s
```
3. Update OpenStackDataPlaneNodeSet
```bash
oc apply -f openstackdataplanenodeset.yaml
```
4. Recreate OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc delete -f openstackdataplanedeployment.yaml
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd openstack-edpm-ipam --for condition=Ready --timeout=720s
```
5. Force Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
