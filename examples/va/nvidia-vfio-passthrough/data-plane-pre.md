# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane/README.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nvidia-vfio-passthrough directory
```
cd architecture/examples/va/nvidia-vfio-passthrough
```
Edit the `edpm/nodeset/values.yaml` and `edpm/deployment/values.yaml` files to suit your environment.

In `edpm/nodeset/values.yaml`, pay special attention to the `baremetalhosts` section. You will need to provide details for each of your baremetal compute nodes, including:
- `bmc.address`: The IP address of the Baseboard Management Controller (BMC).
- `bootMACAddress`: The MAC address of the network interface that the node will use to PXE boot.
- Other parameters as described in the main [README.md](README.md).
```
vi edpm/nodeset/values.yaml
vi edpm/deployment/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build edpm/nodeset > dataplane-nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > dataplane-deployment.yaml
```

## Create CRs and do initial deployment
Create the nodeset CR
```
oc apply -f dataplane-nodeset.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```
