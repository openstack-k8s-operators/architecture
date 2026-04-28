# Configure and deploy the initial data plane to prepare for Ceph installation

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the nova05epsilon directory

```shell
cd architecture/examples/dt/nova/nova05epsilon
```

Edit the [edpm-pre-ceph/nodeset/values.yaml](edpm-pre-ceph/nodeset/values.yaml)
file to suit your environment.

```shell
vi edpm-pre-ceph/nodeset/values.yaml
```

Pay special attention to:
- `baremetalhosts` section: BMC addresses, boot MAC addresses, root device hints
- `edpm_kernel_args`: GPU vendor/product IDs for VFIO passthrough
- `edpm_tuned_isolated_cores`: CPU cores to isolate for VM pinning
- `nova.pci.conf`: PCI device_spec entries for each GPU
- `edpm_ceph_hci_pre_enabled_services`: Ceph services to pre-configure
- All EDPM nodes use `subnetName: subnet2` (site4 DCN subnet) -- update the
  CHANGEME CIDRs in both `edpm-pre-ceph/nodeset/values.yaml` and
  `control-plane/networking/nncp/values.yaml` to match site4's actual network

### Create the BareMetalHost CRs

Create the `bmc-secret` secret with BMC credentials:

```shell
oc create secret generic bmc-secret --from-literal=username=CHANGEME --from-literal=password=CHANGEME
```

Generate the BareMetalHost CRs:

```shell
kustomize build edpm/baremetalhosts > baremetalhosts.yaml
```

Apply the BareMetalHost CRs:

```shell
oc apply -f baremetalhosts.yaml
```

Wait for BareMetalHosts to become available:

```shell
oc get bmh -w
```

### Configure and deploy the pre-ceph dataplane

Generate the dataplane nodeset CR:

```shell
kustomize build edpm-pre-ceph/nodeset > dataplane-nodeset.yaml
```

Apply the nodeset CR:

```shell
oc apply -f dataplane-nodeset.yaml
```

Wait for nodeset setup to finish:

```shell
oc wait osdpns gpu-computes-edpm --for condition=SetupReady --timeout=600s
```

Generate and apply the deployment CR:

```shell
kustomize build edpm-pre-ceph/deployment > dataplane-deployment.yaml
oc apply -f dataplane-deployment.yaml
```

Wait for deployment to finish:

```shell
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=40m
```

After the NVIDIA drivers have been blacklisted and kernel args updated,
EDPM hosts will be automatically rebooted.

## Install Ceph

At this point, install Ceph on the compute nodes. The Ceph installation
is not managed by OpenStack K8S operators.
