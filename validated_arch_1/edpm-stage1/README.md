# Stage 5

Deploy the initial data plane to prepare for CephHCI installation

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
