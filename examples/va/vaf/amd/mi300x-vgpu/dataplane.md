# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed.
- The AMD GIM driver is installed on the pre-provisioned EDPM host.

## Initialize

Switch to the `openstack` namespace:
```
oc project openstack
```

Change to the `mi300x-vgpu/edpm` directory:
```
cd architecture/examples/va/vaf/amd/mi300x-vgpu/edpm
```

Edit the nodeset values to match your environment (IPs, MACs, PCI BDFs, SSH keys):
```
vi nodeset/values.yaml
```

> **NOTE**: Defaults provide 8 VFs per PF, CPX mode - adjust as needed for your vGPU slicing configuration.

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

After a successful deployment, confirm that Nova sees the MI300X VFs as PCI resources:
```
oc rsh openstackclient openstack resource provider inventory list <rp-uuid>
```

You should see `CUSTOM_PCI_<product_id>` resource class entries for each VF.

## Finalize Nova computes

Ask Nova to discover all compute hosts:
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
