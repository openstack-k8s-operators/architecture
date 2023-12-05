# Stage 5

Deploy the initial data plane to prepare for CephHCI installation

## Notes

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

### Todo
- Update to use kustomize
