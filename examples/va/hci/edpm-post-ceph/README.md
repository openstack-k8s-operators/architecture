# EDPM Post Ceph

Finish deploying the data plane after Ceph is available

## Notes

Assumes that a Ceph cluster is available.

At this stage the CRs in this directory need to be edited to match the
values in your environment. Look for `#CHANGEME` comments in each CR
and update them accordingly. In the future this will not be necessary
when this `edpm-pre-ceph` and `edpm-post-ceph` directories are updated
to use `kustomize`.

During this stage the OpenStackDataPlaneNodeSet
(openstackdataplanenodeset.yaml) and OpenStackControlPlane
(openstackcontrolplane.yaml) are updated. New instances of these
services are not created. Thus, if you have modified these CRs beyond
after [creating the OpenStackControlPlane](../control-plane.md) or after
[creating the OpenStackDataPlaneNodeSet](../edpm-pre-ceph/README.md),
then your personal changes could be lost when you run `oc apply` as
described below. To avoid this, `diff` the files and apply the changes
using `oc edit` or `oc patch` during steps 2 and 3 below.

```bash
cd architecture/examples/va/hci
diff -u control-plane.yaml edpm-post-ceph/openstackcontrolplane.yaml
diff -u edpm-pre-ceph/openstackdataplanenodeset.yaml edpm-post-ceph/openstackdataplanenodeset.yaml
```

## Steps

1. Create Secrets
```bash
oc apply -f ceph_secret.yaml -f nova_ceph.yaml -f nova_migration_ssh_key.yaml
```
2. Update OpenStackControlPlane and wait for it to finish
```bash
oc apply -f openstackcontrolplane.yaml
oc wait osctlplane controlplane --for condition=Ready --timeout=300s
```
3. Update OpenStackDataPlaneNodeSet
```bash
oc apply -f openstackdataplanenodeset.yaml
```
4. Create a post-Ceph OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd deployment-post-ceph --for condition=Ready --timeout=720s
```
5. Ask Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
