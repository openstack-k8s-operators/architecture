# Stage 6

Finish deploying the data plane after Ceph is available

## Notes

Assumes that a Ceph cluster is available

During stage 6 the OpenStackDataPlaneNodeSet (openstackdataplanenodeset.yaml)
and OpenStackControlPlane (openstackcontrolplane.yaml) are updated. New instances
of these services are not created in stage 6. Thus, if you have modified these CRs
beyond when they were created (stage 4 for OpenStackControlPlane and stage 5 for
OpenStackDataPlaneNodeSet), then your personal changes could be lost when you run
`oc apply` as described below. To avoid this, `diff` the files and apply the changes
using `oc edit` or `oc patch` during steps 3 and 4 below.

```bash
diff -u stage4/openstackcontrolplane.yaml stage6/openstackcontrolplane.yaml
diff -u stage5/openstackdataplanenodeset.yaml stage6/openstackdataplanenodeset.yaml
```

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

### Todo
- Update to use kustomize
