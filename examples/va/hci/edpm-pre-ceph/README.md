# EDPM Pre Ceph

Deploy the initial data plane to prepare for CephHCI installation

## Notes

At this stage the CRs in this directory need to be edited to match the
values in your environment. Look for `#CHANGEME` comments in each CR
and update them accordingly. In the future this will not be necessary
when this `edpm-pre-ceph` and `edpm-post-ceph` directories are updated
to use `kustomize`.

Requires 3 pre-provisioned compute nodes that are accessible via the control plane IPs
enumerated in step 2's `OpenStackDataPlaneNodeSet` using the SSH credentials provided
in step 1's `Secret`.

## Steps

1. Create SSH Secret
```bash
oc apply -f dataplanesshsecret.yaml
```
2. Create OpenStackDataPlaneNodeSet
```bash
oc apply -f openstackdataplanenodeset.yaml
```
3. Create pre-Ceph OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd deployment-pre-ceph --for condition=Ready --timeout=720s
```
