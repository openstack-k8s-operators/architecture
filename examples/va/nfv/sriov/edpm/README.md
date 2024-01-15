# SRIOV EDPM

Deploy the SRIOV-enabled data plane

## Notes

At this stage the CRs in this directory need to be edited to match the
values in your environment. Look for `#CHANGEME` comments in each CR
and update them accordingly. In the future this will not be necessary
when this is updated to use `kustomize`.

## Steps

1. Create Secrets
```bash
oc apply -f dataplanesshsecret.yaml -f nova_migration_ssh_key.yaml
```
2. Create SRIOV ConfigMaps and associated OpenStackDataPlaneService
```bash
oc apply -f nova_sriov.yaml
```
3. Create OpenStackDataPlaneNodeSet
```bash
oc apply -f openstackdataplanenodeset.yaml
```
4. Create OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd edpm-sriov-deployment --for condition=Ready --timeout=720s
```
