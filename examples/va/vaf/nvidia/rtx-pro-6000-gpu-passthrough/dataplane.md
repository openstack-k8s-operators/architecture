# Configuring and deploying the dataplane

## Assumptions

The [control plane](control-plane.md) has been created and successfully deployed.

## Initialize

Switch to the `openstack` namespace:
```
oc project openstack
```

Change to the `rtx-pro-6000-gpu-passthrough/edpm` directory:
```
cd architecture/examples/va/vaf/nvidia/rtx-pro-6000-gpu-passthrough/edpm
```

Edit the baremetalhosts and nodeset values to match your environment (BMC/BareMetalHost,
IPs, MACs, GPU PCI addresses, SSH keys):
```
vi baremetalhosts/values.yaml
vi nodeset/values.yaml
```

Set the iDRAC credentials the BareMetalHost uses to provision the node by editing
the [bmc-secret.env](edpm/baremetalhosts/bmc-secret.env) *env* file:
```
vi baremetalhosts/bmc-secret.env
```

## Provision the BareMetalHost

Generate the BareMetalHost CRs:
```
kustomize build baremetalhosts > baremetalhosts.yaml
```

Apply them and wait for the host to reach `available`:
```
oc apply -f baremetalhosts.yaml
oc wait bmh edpm-compute-0 --for jsonpath='{.status.provisioning.state}'=available --timeout=600s
```

## Deploy the nodeset

Generate the dataplane nodeset CR:
```
kustomize build nodeset > dataplane-nodeset.yaml
```

Apply the nodeset:
```
oc apply -f dataplane-nodeset.yaml
```

Wait for the nodeset setup to finish:
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

## Deploy the dataplane

Generate the dataplane deployment CR:
```
kustomize build deployment > dataplane-deployment.yaml
```

Apply the deployment:
```
oc apply -f dataplane-deployment.yaml
```

Wait for the dataplane deployment to finish:
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```

## Verify GPU availability

After a successful deployment, confirm the GPU is bound to `vfio-pci` on the host:
```
lspci -nnk -d 10de:2bb5   # Kernel driver in use: vfio-pci
```

Confirm that Nova reports the GPU as a PCI resource in Placement. First find the
compute's resource provider UUID, list its provider tree, and inspect the PCI
resource provider's inventory:
```
oc rsh openstackclient openstack resource provider list
oc rsh openstackclient openstack resource provider list --in-tree <rp-uuid>
oc rsh openstackclient openstack resource provider inventory list <pci-rp-uuid>
```

You should see a `CUSTOM_PCI_10DE_2BB5` resource class entry in each GPU
provider's inventory.

## Finalize Nova computes

Ask Nova to discover all compute hosts:
```bash
oc rsh nova-cell1-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
